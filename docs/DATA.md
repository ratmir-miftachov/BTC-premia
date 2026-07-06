# Data Requirements

This repository intentionally does not commit the raw option data, proprietary intermediate files, generated CSV/XLSX outputs, or pickled artifacts used in the paper. The `.gitignore` excludes these file types so users can place local data in the expected folders without accidentally committing it.

## Expected Layout

The machine-readable source of truth is `config/data_manifest.yaml`. The historical scripts use these repo-relative folders:

- `Data/`: raw and processed market data, including files such as `IR_daily.csv`, `BTC_USD_Quandl_2011_2023.csv`, and processed option panels.
- `SVI/v1/`: SVI parameter and R2 result files consumed by IV-surface scripts.
- `IV/IV_SVI/...` and `IV/IV_surface_SVI/...`: generated IV curve and surface files.
- `Q_from_pure_SVI/...`: generated per-date Q-density files.
- `Q_matrix/...`: filtered Q-density matrices by maturity.
- `Clustering/...`: cluster assignments and common-date files.
- `RiskPremia/...`: premium, pricing-kernel, and variance-risk-premium inputs used by MATLAB scripts.
- `Lower_Bound/...`: generated lower-bound outputs.
- `results/figures/`: generated figures from newer Python helpers.

Some newer utilities use lowercase folders under `data/`, for example `data/iv_matrices/IR0`, `data/iv_surfaces`, `data/q_densities`, and `data/risk_premia`. The pipeline helper reports which inputs are missing for each stage.

Validate local data availability with:

```bash
python scripts/check_reproducibility.py --manifest config/data_manifest.yaml
python scripts/run_full_pipeline.py --steps validate
```

Use `--strict` when you want missing required files to produce a non-zero exit code.

## External Data Base

If you keep data outside the Git checkout, set `BTC_PREMIA_BASE` before running Python scripts:

```bash
export BTC_PREMIA_BASE=/path/to/btc-premia-data
```

The code will then resolve legacy input and output folders under that base path.

## Missing Sources

The repository does not currently provide public download instructions for the raw option data or for all generated paper intermediates. It also references `src/Q_from_IV.R` for Q-density estimation, but that R source file is not present.

## Public Fixtures

The `tests/fixtures` directory contains tiny synthetic CSV files used only for smoke tests. They are not paper data and should not be used for empirical results.

## Provenance

Python stages that generate new outputs should write a JSON provenance sidecar containing input hashes, parameters, Python and package versions, platform, and timestamp. Existing provenance helpers live in `src/utils/data_utils.py`.
