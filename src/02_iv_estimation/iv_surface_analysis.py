# IV surface
"""Generate IV curves using estimated SVI parameters."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT / "src"))

from utils.data_utils import write_provenance


DEFAULT_BASE_DIR = Path(os.environ.get("BTC_PREMIA_BASE", PROJECT_ROOT)).expanduser()
DEFAULT_SVI_DIR = DEFAULT_BASE_DIR / "SVI" / "v1"
DEFAULT_OUTPUT_DIR = DEFAULT_BASE_DIR / "IV" / "IV_SVI" / "Tau-independent" / "unique" / "moneyness_step_0d01"


def svi_model_ind(theta, k):
    """Time-to-maturity independent SVI model."""
    base_params = np.array(theta[:5])
    a, b, rho, m, sigma = base_params
    return a + b * (rho * (k - m) + np.sqrt((k - m) ** 2 + sigma ** 2))


def process_date(date_val, paras, ttms, k_new, output_dir):
    """Process one date and write its IV surface."""
    match = re.search(r'(\d{4}-\d{2}-\d{2})', date_val)
    if not match:
        print(f"Skipping {date_val}: no YYYY-MM-DD date found.")
        return pd.DataFrame()

    date = match.group(0)
    print(f"Estimate IV for date {date}.")
    all_ivs = pd.DataFrame()

    for ttm in ttms:
        theta = paras.loc[(paras['Date'] == date_val) & (paras['tau'] == ttm)]
        if theta.empty:
            continue
        theta = theta.drop(theta.columns[0:2], axis=1)
        theta = np.squeeze(theta.values)

        iv = np.sqrt(svi_model_ind(theta, k_new))
        iv_dict = {str(k): [value] for k, value in zip(k_new, iv)}
        iv_dict['Date'] = date
        iv_dict['TTM'] = ttm
        iv_df = pd.DataFrame(iv_dict)

        if iv_df.isna().any().any():
            print(f"NaN values found in IV for {date_val} at TTM {ttm}.")
            continue

        cols = ['Date', 'TTM'] + [col for col in iv_df if col not in ('Date', 'TTM')]
        all_ivs = pd.concat([all_ivs, iv_df[cols]], ignore_index=True)

    all_ivs = all_ivs.sort_values(by=['Date', 'TTM'])
    output_path = output_dir / f'interpolated_{date}_allR2.csv'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    all_ivs.to_csv(output_path, index=False)
    return all_ivs


def run(svi_dir: Path, output_dir: Path, n_jobs: int) -> None:
    """Generate IV surfaces for all dates found in SVI parameter outputs."""
    svi_dir = svi_dir.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()

    results_path = svi_dir / 'svi_Tau-Ind_Mon-Uni_iv_and_r2_results.csv'
    paras_path = svi_dir / 'svi_Tau-Ind_Mon-Uni_paras.csv'
    df1 = pd.read_csv(results_path)
    df2 = pd.read_csv(paras_path)

    paras = df2.loc[df1.index].copy()
    paras.columns.values[0] = 'Date'
    paras.columns = paras.columns.str.strip()

    k_new = np.linspace(-1, 1, 201)
    ttms = list(range(3, 121))
    unique_dates = paras['Date'].unique()
    print("Files to process:", unique_dates)

    all_ivs_list = Parallel(n_jobs=n_jobs)(
        delayed(process_date)(date_val, paras, ttms, k_new, output_dir)
        for date_val in unique_dates
    )

    all_ivs_concat = pd.concat(all_ivs_list, ignore_index=True)
    output_path_all = output_dir / 'interpolated_all_dates_allR2.csv'
    output_path_all.parent.mkdir(parents=True, exist_ok=True)
    all_ivs_concat.to_csv(output_path_all, index=False)
    write_provenance(
        output_dir / "iv_surface_analysis_provenance.json",
        script=__file__,
        inputs=[results_path, paras_path],
        parameters={
            "svi_dir": str(svi_dir),
            "output_dir": str(output_dir),
            "n_jobs": n_jobs,
            "ttm_min": min(ttms),
            "ttm_max": max(ttms),
        },
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate IV surfaces from SVI parameters.")
    parser.add_argument("--svi-dir", type=Path, default=DEFAULT_SVI_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--n-jobs", type=int, default=-2)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run(args.svi_dir, args.output_dir, args.n_jobs)


if __name__ == "__main__":
    main()
