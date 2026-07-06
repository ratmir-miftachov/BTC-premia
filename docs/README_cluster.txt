# Clustering Workflow

The market-regime clustering workflow lives in `src/04_clustering` and consumes filtered Q-density matrices for multiple maturities.

Main files:

- `market_regime_clustering.py`: performs CLR transformation, Ward-linkage clustering, and PCA-style diagnostic plots from Q matrices.
- `dimensionality_reduction_umap.py`: produces UMAP visualizations of the clustered Q-density states. Set `BTC_PREMIA_RANDOM_SEED` to control UMAP randomness.

The required Q-matrix files are declared in `config/data_manifest.yaml`. A tiny public fixture is available under `tests/fixtures/Q_matrix` and is exercised by:

```bash
python -m unittest discover -s tests
```
