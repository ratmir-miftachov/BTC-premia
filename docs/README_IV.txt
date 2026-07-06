# Implied Volatility Workflow

The implied-volatility workflow lives in `src/02_iv_estimation` and consumes ignored option/IV matrix data. The current scripts are research-stage Python scripts; run the reproducibility checker first to see which inputs are present:

```bash
python scripts/check_reproducibility.py --manifest config/data_manifest.yaml
python scripts/run_full_pipeline.py --dry-run --steps iv
```

Main files:

- `svi_tau_dependent_estimation.py`: estimates tau-dependent SVI parameters from `IV*.csv` matrices. It supports `--input-dir`, `--output-dir`, `--plots-dir`, and `--seed`.
- `iv_surface_analysis.py`: builds tau-independent IV curves from `SVI/v1` parameter outputs. It supports `--svi-dir`, `--output-dir`, and `--n-jobs`.
- `linear_ttm_interpolation.py`: interpolates generated IV curves across maturities.
- `svi_surface_construction.py`: legacy construction/averaging script for selected SVI surfaces.

Expected inputs and outputs are listed in `config/data_manifest.yaml`.
