# Risk Premia in Bitcoin Market
This repository contains the implementation code for the paper [**"Risk Premia in the Bitcoin Market"**](https://arxiv.org/abs/2410.15195) by Caio Almeida, Maria Grith, Ratmir Miftachov and Zijin Wang.

## Abstract
Based on options and realized returns, we analyze risk premia in the Bitcoin market through the lens of the Pricing Kernel (PK). We identify that: 1) The projected PK into Bitcoin returns is W-shaped and steep in the negative returns region; 2) Negative Bitcoin returns account for 33% of the total Bitcoin index premium (BP) in contrast to 70% of S&P500 equity premium explained by negative returns. Applying a novel clustering algorithm to the collection of estimated Bitcoin risk-neutral densities, we find that risk premia vary over time as a function of two distinct market volatility regimes. In the low-volatility regime, the PK projection is steeper for negative returns. It has a more pronounced W-shape than the unconditional one, implying particularly high BP for both extreme positive and negative returns and a high Variance Risk Premium (VRP). In high-volatility states, the BP attributable to positive and negative returns is more balanced, and the VRP is lower. Overall, Bitcoin investors are more worried about variance and downside risk in low-volatility states.


## Analysis 

### 1. **Data Preprocessing** 
- **Files**: `options_data_loader.py`, `summary_statistics.py`
- **Function**: Load raw options data, apply filters, calculate descriptive statistics
- **Outputs**: Cleaned datasets, summary reports

### 2. **Implied Volatility Estimation** 
- **Files**: `svi_parameter_estimation.py`, `iv_surface_construction.py`, `interpolation_methods.py`, `daily_iv_processing.py`
- **SVI Model**: Stochastic Volatility Inspired parameterization for each trading day
- **Outputs**: SVI parameters, complete IV surfaces, R² statistics

### 3. **Q-Density Estimation** 
- **Files**: `q_density_estimation.py`, `density_filtering.py`  
- **Method**: Breeden-Litzenberger formula implementation with R integration
- **Filtering**: Multiple time-to-maturity specifications (5, 9, 14, 27, 45 days)
- **Outputs**: Risk-neutral probability densities

### 4. **Market Regime Clustering** 
- **Files**: `market_regime_clustering.py`, `dimensionality_reduction.py`
- **Transformation**: Centered Log-Ratio (CLR) for compositional data
- **Algorithm**: Ward linkage hierarchical clustering 
- **Regime Types**: High-volatility (HV) vs Low-volatility (LV) market states

### 5. **Risk Premium Analysis** 
- **Files**: `bitcoin_premium_calculation.py`, `variance_risk_premium.py`, `lower_bounds_analysis.py`, `state_dependent_analysis.py`, `premium_decomposition.py`, `risk_premium_reporting.py`
- **Bitcoin Premium (BP)**: μ_P - μ_Q analysis across return spectrum
- **Variance Risk Premium (VRP)**: Var_Q - Var_P calculations
- **Theoretical Bounds**: Implementation of Chabi-Yo & Loudis (2020) framework
- **Regime Analysis**: State-dependent risk premium behavior

### 6. **Volatility Index** 
- **Files**: `bvix_calculation.py`
- **BVIX**: Model-free Bitcoin volatility index following VIX methodology
- **Integration**: Multi-maturity variance swap rate calculation

### 7. **Visualization** 
- **Files**: various plots of the paper
  - `iv_surface_plotting.py`: 3D implied volatility surfaces
  - `q_density_plotting.py`: Risk-neutral vs physical density comparisons  
  - `bitcoin_premium_plotting.py`: Risk premium time series and distributions
  - `variance_risk_premium_plotting.py`: VRP analysis and regime comparison
  - `clustering_visualization.py`: PCA/UMAP projections and regime plots


