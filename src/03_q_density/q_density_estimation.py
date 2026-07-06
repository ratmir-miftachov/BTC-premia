# Q density
"""Estimate risk-neutral Q densities from generated IV surfaces."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT / "src"))

from utils.data_utils import write_provenance


DEFAULT_BASE_PATH = Path(os.environ.get("BTC_PREMIA_BASE", PROJECT_ROOT)).expanduser()
DEFAULT_R_SOURCE_PATH = PROJECT_ROOT / "src" / "Q_from_IV.R"
DEFAULT_IV_DIR = DEFAULT_BASE_PATH / "IV" / "IV_surface_SVI" / "Tau-independent" / "unique" / "moneyness_step_0d01"
DEFAULT_OUT_PATH = DEFAULT_BASE_PATH / "Q_from_pure_SVI" / "Tau-independent" / "unique" / "moneyness_step_0d01"
DEFAULT_INTEREST_RATE_PATH = DEFAULT_BASE_PATH / "Data" / "IR_daily.csv"


def estimate_Q(log_ret, IV, dIVdr, d2IVdr2, rf, tau, r_obj, out_dir):
    """Call the R implementation that computes Q density from IV derivatives."""
    from rpy2 import robjects

    try:
        moneyness, spd, logret, spd_logret, volas, cdf_m, cdf_ret, sigmas1, sigmas2 = r_obj.estimate_Q_from_IV(
            robjects.FloatVector(log_ret),
            robjects.FloatVector(IV[0]),
            robjects.FloatVector(dIVdr),
            robjects.FloatVector(d2IVdr2),
            robjects.FloatVector(rf),
            robjects.FloatVector([tau]),
            robjects.StrVector([str(out_dir)])
        )
        moneyness = np.array(moneyness) - 1
        return pd.DataFrame({
            'm': moneyness,
            'spdy': spd,
            'ret': logret,
            'spd_ret': spd_logret,
            'volatility': volas,
            'cdf_m': cdf_m,
            'cdf_ret': cdf_ret,
            'sigma_prime': sigmas1,
            'sigma_double_prime': sigmas2
        })
    except Exception as e:
        print('Exception in estimate_Q:', e)
        return None


def process_file(file, ttm, out_path, interest_rate_data, iv_dir, r_source_path):
    tau = ttm / 365.0
    out_dir = out_path / f'tau_{ttm}'
    out_dir.mkdir(parents=True, exist_ok=True)

    file_path = iv_dir / file

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return f"Failed to read file {file}: {e}"

    if 'TTM' not in df.columns:
        return f"TTM column not found in {file}."
    if ttm not in df['TTM'].unique():
        return f"TTM value {ttm} not in file {file}."

    df = df[df["TTM"] == ttm]

    try:
        date = file.split("_")[1]
    except IndexError:
        return f"Filename {file} does not contain expected date info."

    try:
        logret = np.log(df.columns[2:].astype(float) + 1 + 1e-10).to_numpy()
    except Exception as e:
        return f"Error converting column names to floats for log returns in file {file}: {e}"

    iv_filtered = df[df['Date'] == date]
    if iv_filtered.empty:
        return f"No data for date {date} in file {file}."
    IV = iv_filtered.drop(columns=['Date', 'TTM']).to_numpy()

    try:
        dIVdr = (IV[0][2:] - IV[0][:-2]) / (logret[2:] - logret[:-2])
        dIVdr = [float('nan')] + list(dIVdr) + [float('nan')]
        dIVdr[0] = (IV[0][1] - IV[0][0]) / (logret[1] - logret[0])
        dIVdr[-1] = (IV[0][-1] - IV[0][-2]) / (logret[-1] - logret[-2])
    except Exception as e:
        return f"Error computing first derivative for file {file}: {e}"

    try:
        d2IVdr2 = (IV[0][2:] - 2 * IV[0][1:-1] + IV[0][:-2]) / ((logret[2:] - logret[:-2]) ** 2)
        d2IVdr2 = [float('nan')] + list(d2IVdr2) + [float('nan')]
        d2IVdr2[0] = (IV[0][2] - 2 * IV[0][1] + IV[0][0]) / ((logret[1] - logret[0]) ** 2)
        d2IVdr2[-1] = (IV[0][-1] - 2 * IV[0][-2] + IV[0][-3]) / ((logret[-1] - logret[-2]) ** 2)
    except Exception as e:
        return f"Error computing second derivative for file {file}: {e}"

    rf = interest_rate_data.interest_rate[interest_rate_data['date'] == date].to_numpy()
    if rf.size == 0:
        return f"No risk-free rate data for date {date} in file {file}."

    try:
        from rpy2 import robjects
        r_obj = robjects.r
        r_obj.source(str(r_source_path))
    except Exception as e:
        return f"Error initializing R in file {file}: {e}"

    spd_btc = estimate_Q(logret.tolist(), IV, dIVdr, d2IVdr2, rf, tau, r_obj, out_dir)
    if spd_btc is None:
        return f"Failed to compute Q for date {date} in file {file}."

    try:
        output_file = out_dir / f"btc_Q_{date}.csv"
        spd_btc.to_csv(output_file, index=False, float_format="%.4f")
    except Exception as e:
        return f"Error saving CSV for date {date} in file {file}: {e}"

    return f"Successfully processed file {file} for date {date}"


def load_interest_rates(path: Path) -> pd.DataFrame:
    interest_rate_data = pd.read_csv(path)
    interest_rate_data = interest_rate_data.rename(columns={'index': 'date', 'DTB3': 'interest_rate'})
    if "date" not in interest_rate_data.columns or "interest_rate" not in interest_rate_data.columns:
        raise ValueError(f"Interest rate file must include date and interest_rate columns: {path}")
    interest_rate_data['interest_rate'] = interest_rate_data['interest_rate'] / 100
    return interest_rate_data


def run_parallel_processing(iv_dir: Path,
                            out_path: Path,
                            interest_rate_path: Path,
                            r_source_path: Path,
                            ttm_start: int,
                            ttm_end: int,
                            n_jobs: int) -> None:
    iv_dir = iv_dir.expanduser().resolve()
    out_path = out_path.expanduser().resolve()
    interest_rate_path = interest_rate_path.expanduser().resolve()
    r_source_path = r_source_path.expanduser().resolve()

    if not r_source_path.exists():
        raise FileNotFoundError(f"Missing R source required for Q-density estimation: {r_source_path}")

    interest_rate_data = load_interest_rates(interest_rate_path)
    files = sorted([f for f in os.listdir(iv_dir) if f.endswith(".csv")])
    ttm_list = range(ttm_start, ttm_end + 1)

    for ttm in ttm_list:
        print(f"Processing TTM = {ttm} ...")
        results = Parallel(n_jobs=n_jobs)(
            delayed(process_file)(file, ttm, out_path, interest_rate_data, iv_dir, r_source_path)
            for file in files
        )
        for result in results:
            print(result)

    write_provenance(
        out_path / "q_density_estimation_provenance.json",
        script=__file__,
        inputs=[interest_rate_path, r_source_path, *[iv_dir / file for file in files]],
        parameters={
            "iv_dir": str(iv_dir),
            "out_path": str(out_path),
            "ttm_start": ttm_start,
            "ttm_end": ttm_end,
            "n_jobs": n_jobs,
        },
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Estimate Q densities from IV surfaces.")
    parser.add_argument("--iv-dir", type=Path, default=DEFAULT_IV_DIR)
    parser.add_argument("--out-path", type=Path, default=DEFAULT_OUT_PATH)
    parser.add_argument("--interest-rate-path", type=Path, default=DEFAULT_INTEREST_RATE_PATH)
    parser.add_argument("--r-source", type=Path, default=DEFAULT_R_SOURCE_PATH)
    parser.add_argument("--ttm-start", type=int, default=3)
    parser.add_argument("--ttm-end", type=int, default=120)
    parser.add_argument("--n-jobs", type=int, default=-2)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_parallel_processing(
        iv_dir=args.iv_dir,
        out_path=args.out_path,
        interest_rate_path=args.interest_rate_path,
        r_source_path=args.r_source,
        ttm_start=args.ttm_start,
        ttm_end=args.ttm_end,
        n_jobs=args.n_jobs,
    )


if __name__ == "__main__":
    main()
