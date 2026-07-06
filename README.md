# Risk Premia in Bitcoin Market

This repository contains research code for the paper [**"Risk Premia in the Bitcoin Market"**](https://arxiv.org/abs/2410.15195) by Caio Almeida, Maria Grith, Ratmir Miftachov and Zijin Wang.

The codebase is a mixed Python and MATLAB research artifact. The repository does not include the raw, private, or large intermediate data files used in the paper, so a fresh clone cannot reproduce every table and figure end to end without supplying those inputs.

## Repository Structure

- `config/parameters.yaml`: shared parameter values for filtering, SVI estimation, clustering, risk-premium analysis, and output formatting.
- `scripts/run_full_pipeline.py`: workflow inspection CLI. It lists known stages, reports required inputs, and fails clearly for manual or blocked stages instead of logging fake success.
- `src/01_data_preprocessing`: MATLAB summary-statistics scripts for option data.
- `src/02_iv_estimation`: Python SVI estimation, IV-surface construction, and maturity interpolation scripts.
- `src/03_q_density`: Python Q-density estimation and filtering scripts. The estimation stage expects an external R routine, `src/Q_from_IV.R`, which is not currently present in this repository.
- `src/04_clustering`: Python market-regime clustering and UMAP visualization scripts.
- `src/05_risk_analysis`: Python lower-bound analysis plus MATLAB scripts for Bitcoin premium, pricing-kernel, variance-risk-premium, and market-state analysis.
- `src/06_volatility`: Python BVIX calculation script.
- `src/07_visualization`: Python and MATLAB plotting scripts for IV, Q-density, clustering, BVIX, and lower-bound figures.
- `src/utils`: shared Python utility functions.

## Environment

Use Python 3.10+ for the Python scripts.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Several stages also require MATLAB. Q-density estimation additionally depends on an R bridge (`rpy2`) and the missing `src/Q_from_IV.R` routine. Optional analysis extras such as notebooks, UMAP, and Plotly are documented in `requirements.txt`.

## Data

Large and private data files are intentionally ignored by `.gitignore` (`*.csv`, `*.xlsx`, `*.pkl`, and related formats). See [`docs/DATA.md`](docs/DATA.md) for the expected input and output layout.

Most legacy scripts use paper-era directory names such as `Data`, `SVI`, `IV`, `Q_matrix`, `RiskPremia`, and `Lower_Bound`. Newer helpers also expose lowercase paths under `data/` and `results/`. If the data lives outside the checkout, set:

```bash
export BTC_PREMIA_BASE=/path/to/btc-premia-data
```

before running the legacy Python scripts that now support repo-relative defaults.

## Workflow Status

Inspect the current workflow map:

```bash
python scripts/run_full_pipeline.py --list-steps
python scripts/run_full_pipeline.py --dry-run --steps all
```

The pipeline helper currently documents the workflow and validates missing inputs. It does not run the full paper pipeline automatically because several stages are manual MATLAB workflows or require ignored/private data. Running without `--dry-run` will fail clearly when selected stages are blocked or manual.

High-level stages:

1. **Data preprocessing**: MATLAB scripts in `src/01_data_preprocessing`.
2. **Implied volatility estimation**: Python scripts in `src/02_iv_estimation`.
3. **Q-density estimation**: Python/R workflow in `src/03_q_density`.
4. **Market-regime clustering**: Python scripts in `src/04_clustering`.
5. **Risk-premium analysis**: mixed Python and MATLAB scripts in `src/05_risk_analysis`.
6. **Bitcoin volatility index**: Python script in `src/06_volatility`.
7. **Visualization**: mixed Python and MATLAB scripts in `src/07_visualization`.

## Reproducibility Notes

- The README now reflects actual file names in the repository rather than planned or historical names.
- Python scripts no longer require editing machine-local absolute paths before use; use repo-relative defaults or `BTC_PREMIA_BASE`.
- MATLAB scripts are preserved as paper-analysis scripts. Some still expect historical folder names and should be run manually with the required data layout.
- The conservative cleanup removed only an empty, unreferenced placeholder file from `docs/`.
