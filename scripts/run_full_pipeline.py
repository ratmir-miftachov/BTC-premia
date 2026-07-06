#!/usr/bin/env python3
"""Truthful orchestration helper for the BTC-premia analysis workflow.

The repository contains research scripts from multiple stages of the paper.
This command documents and validates those stages; it does not pretend that
manual MATLAB scripts or missing private data have run successfully.
"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from utils.data_utils import DataPaths, load_config


REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class StepSpec:
    """Metadata for one externally visible pipeline step."""

    name: str
    title: str
    status: str
    description: str
    scripts: tuple[str, ...]
    required_paths: tuple[str, ...] = ()
    automated: bool = False


STEP_ORDER = ("iv", "q_density", "clustering", "risk", "bvix", "viz")

STEP_SPECS: dict[str, StepSpec] = {
    "iv": StepSpec(
        name="iv",
        title="Implied volatility estimation",
        status="blocked-data",
        description=(
            "SVI estimation and IV-surface construction are Python scripts, "
            "but they require ignored option/IV matrix inputs."
        ),
        scripts=(
            "src/02_iv_estimation/svi_tau_dependent_estimation.py",
            "src/02_iv_estimation/iv_surface_analysis.py",
            "src/02_iv_estimation/linear_ttm_interpolation.py",
            "src/02_iv_estimation/svi_surface_construction.py",
        ),
        required_paths=("data/iv_matrices/IR0", "SVI/v1"),
    ),
    "q_density": StepSpec(
        name="q_density",
        title="Risk-neutral density estimation",
        status="blocked-data-r",
        description=(
            "Q-density estimation requires generated IV surfaces, interest-rate "
            "data, and the external R routine referenced by the Python script."
        ),
        scripts=(
            "src/03_q_density/q_density_estimation.py",
            "src/03_q_density/q_density_filtering_parallel.py",
        ),
        required_paths=(
            "IV/IV_surface_SVI/Tau-independent/unique/moneyness_step_0d01",
            "Data/IR_daily.csv",
            "src/Q_from_IV.R",
        ),
    ),
    "clustering": StepSpec(
        name="clustering",
        title="Market regime clustering",
        status="blocked-data",
        description="Clustering requires precomputed Q matrices for several maturities.",
        scripts=(
            "src/04_clustering/market_regime_clustering.py",
            "src/04_clustering/dimensionality_reduction_umap.py",
        ),
        required_paths=("Q_matrix/Tau-independent/unique/moneyness_step_0d01",),
    ),
    "risk": StepSpec(
        name="risk",
        title="Risk-premium analysis",
        status="manual-matlab-and-python",
        description=(
            "Risk-premium figures and decompositions are split across MATLAB "
            "paper scripts and a Python lower-bound script."
        ),
        scripts=(
            "src/05_risk_analysis/theoretical_lower_bounds.py",
            "src/05_risk_analysis/bitcoin_premium_main_analysis.m",
            "src/05_risk_analysis/variance_risk_premium_analysis.m",
            "src/05_risk_analysis/pricing_kernel_analysis.m",
            "src/05_risk_analysis/market_state_analysis.m",
        ),
        required_paths=(
            "Q_matrix/Tau-independent/unique/moneyness_step_0d01",
            "RiskPremia/Tau-independent/unique/moneyness_step_0d01",
            "Data/BTC_USD_Quandl_2011_2023.csv",
        ),
    ),
    "bvix": StepSpec(
        name="bvix",
        title="Bitcoin volatility index",
        status="blocked-data",
        description="BVIX calculation requires ignored option quote files and DVOL data.",
        scripts=("src/06_volatility/bvix_calculation.py",),
        required_paths=("data/bvix/ttm27_new", "Data/deribit-metrics_new.csv"),
    ),
    "viz": StepSpec(
        name="viz",
        title="Visualization",
        status="manual-mixed",
        description=(
            "Visualization scripts consume generated intermediate files and include "
            "both Python and MATLAB scripts."
        ),
        scripts=(
            "src/07_visualization/q_density_iv_combined_plots.py",
            "src/07_visualization/q_density_iv_grid_plots.py",
            "src/07_visualization/r2_tau_date_plotting.py",
            "src/07_visualization/r2_timeseries_plotting.py",
            "src/07_visualization/*.m",
        ),
        required_paths=("results",),
    ),
}


def setup_logging(log_level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(levelname)s: %(message)s",
        handlers=[logging.StreamHandler()],
    )


def expand_steps(steps: Iterable[str]) -> list[str]:
    selected = list(steps)
    if "all" in selected:
        return list(STEP_ORDER)
    return selected


def missing_paths(base_path: Path, step: StepSpec) -> list[Path]:
    return [base_path / path for path in step.required_paths if not (base_path / path).exists()]


def format_step(step: StepSpec, base_path: Path) -> str:
    missing = missing_paths(base_path, step)
    script_list = ", ".join(step.scripts)
    if missing:
        missing_list = "; missing: " + ", ".join(str(path) for path in missing)
    else:
        missing_list = ""
    return (
        f"{step.name}: {step.title}\n"
        f"  status: {step.status}\n"
        f"  scripts: {script_list}\n"
        f"  note: {step.description}{missing_list}"
    )


def print_steps(steps: Iterable[str], base_path: Path) -> None:
    for name in expand_steps(steps):
        print(format_step(STEP_SPECS[name], base_path))


def validate_config(config_path: Path) -> None:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    load_config(str(config_path))


def run_selected_steps(step_names: list[str], base_path: Path) -> int:
    non_automated = []
    blocked = []

    for name in step_names:
        step = STEP_SPECS[name]
        missing = missing_paths(base_path, step)
        if missing:
            blocked.append((step, missing))
        if not step.automated:
            non_automated.append(step)

    for step, paths in blocked:
        logging.error("%s is blocked by missing inputs:", step.name)
        for path in paths:
            logging.error("  %s", path)

    if non_automated:
        logging.error("No selected step is currently executed automatically.")
        logging.error("Use --dry-run or --list-steps to inspect the workflow map.")
        for step in non_automated:
            logging.error("%s remains %s: %s", step.name, step.status, step.description)
        return 1

    logging.info("Selected steps are automated, but no automated steps are registered yet.")
    return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect the BTC-premia analysis workflow")
    parser.add_argument(
        "--config",
        default="config/parameters.yaml",
        help="Configuration file path, relative to --base-path unless absolute.",
    )
    parser.add_argument(
        "--steps",
        nargs="+",
        choices=[*STEP_ORDER, "all"],
        default=["all"],
        help="Pipeline steps to inspect or run.",
    )
    parser.add_argument(
        "--base-path",
        default=str(REPO_ROOT),
        help="Repository or external data base path. Defaults to this checkout.",
    )
    parser.add_argument(
        "--list-steps",
        action="store_true",
        help="Print the known workflow stages and exit.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print selected stages, inputs, and current status without running anything.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    setup_logging(args.log_level)

    base_path = Path(args.base_path).expanduser().resolve()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = base_path / config_path

    validate_config(config_path)
    selected_steps = expand_steps(args.steps)
    paths = DataPaths(base_path)

    logging.debug("Base path: %s", paths.base_path)
    logging.debug("Config: %s", config_path)

    if args.list_steps or args.dry_run:
        print_steps(selected_steps, base_path)
        return 0

    logging.info("Requested BTC-premia steps: %s", ", ".join(selected_steps))
    return run_selected_steps(selected_steps, base_path)


if __name__ == "__main__":
    sys.exit(main())
