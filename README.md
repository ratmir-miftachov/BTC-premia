# Risk Premia in Bitcoin Market

A comprehensive analysis of Bitcoin risk premia using nonparametric methods and market regime identification. This repository contains the complete pipeline for analyzing Bitcoin options data (2017-2022) to extract risk-neutral densities, identify market regimes, and calculate various risk premia measures.

## 🎯 Abstract

We adopt options and realized returns to analyze risk premia in the Bitcoin market. By decomposing the index risk premium into different parts of the return space, we find that negative returns between -60% and -20% explain one-third of the total Bitcoin equity premium (EP). This is not only in contrast to results for the S&P 500 market, for which moderately negative returns explain 70% of the EP, but also challenges conventional macro-finance models based on habit, disasters, and long-run risk explanations. 

By clustering data as a function of risk-neutral variance, we identify that risk premia vary over time directly depending on market conditions. During low-volatility market states, investors are mainly concerned with variance risk. Out-of-the-money options (both puts and calls) are used for insurance purposes, and the pricing kernel is steep and U-shaped. During high-volatility states, investors are primarily concerned with downside risk.

**Authors:** Caio Almeida, Maria Grith, Ratmir Miftachov, Zijin Wang

**Keywords:** Risk Premium, Equity Premium, Variance Risk Premium, Pricing Kernel, Nonparametric Statistics, Cryptocurrency, Bitcoin, Option Returns, Clustering

**Data Coverage:** 2017-2022 Bitcoin options with 2000+ daily IV matrices

## 🏗️ Project Structure

This repository has been professionally organized with clear naming conventions and eliminated duplicates for maintainability:

```
BTC-premia/
├── 📁 data/                          # All data files (2000+ IV matrices, results)
│   ├── raw/                          # Original raw options data  
│   ├── processed/                    # Cleaned data ready for analysis
│   ├── iv_surfaces/                  # Daily IV matrices (2017-2022)
│   │   └── IR0/                      # R² filtered IV matrices  
│   ├── q_densities/                  # Risk-neutral density outputs
│   ├── clusters/                     # Market regime clustering results
│   └── risk_premia/                  # Bitcoin/Variance risk premium outputs
│
├── 📁 src/                           # Source code (30 files, organized by pipeline)
│   ├── 01_data_preprocessing/        # Data loading and summary statistics (2 files)
│   ├── 02_iv_estimation/             # SVI model estimation and surfaces (4 files)
│   ├── 03_q_density/                 # Q-density via Breeden-Litzenberger (2 files)
│   ├── 04_clustering/                # Market regime identification (2 files) 
│   ├── 05_risk_analysis/             # Risk premium calculations (6 files)
│   ├── 06_volatility/                # BVIX calculation (1 file)
│   ├── 07_visualization/             # Plotting and charts (13 files)
│   └── utils/                        # Shared utilities (data, math, config)
│
├── 📁 scripts/                       # Executable analysis scripts
│   └── run_full_pipeline.py          # Master pipeline executor
│
├── 📁 config/                        # Configuration management
│   └── parameters.yaml               # Centralized parameter configuration
│
├── 📁 results/                       # Generated analysis outputs
├── 📁 docs/                          # Documentation and methodology
├── 📁 tests/                         # Unit tests for validation
├── 📁 notebooks/                     # Jupyter notebooks for exploration
└── requirements.txt                  # Python dependencies
```

### 🧹 Codebase Improvements

This repository has been extensively reorganized and cleaned:

- **File Reduction**: 42 → 30 source files (removed 12 duplicates)
- **Clear Naming**: Eliminated cryptic codes (S0_, S1_, S2_) in favor of descriptive names
- **Consolidation**: Combined parameter variations into single parameterized files
- **Professional Structure**: Industry-standard data science project organization
- **No Duplicates**: Systematic removal of redundant implementations

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** with scientific computing packages
- **R 4.0+** (for numerical integration in Q-density estimation)  
- **MATLAB R2020a+** (for specialized visualization scripts)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd BTC-premia
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install R packages** (required for Q-density estimation):
   ```r
   # In R console
   install.packages(c("stats", "utils", "splines"))
   ```

### Running the Analysis

#### Option 1: Complete Pipeline (Recommended)
```bash
# Run full analysis pipeline with default parameters
python scripts/run_full_pipeline.py

# Run with custom configuration
python scripts/run_full_pipeline.py --config config/custom_parameters.yaml

# Run with specific date range
python scripts/run_full_pipeline.py --start-date 2017-07-01 --end-date 2018-12-31
```

#### Option 2: Selective Pipeline Execution
```bash
# Run only IV estimation and surface construction
python scripts/run_full_pipeline.py --steps iv,surfaces

# Run clustering and risk analysis
python scripts/run_full_pipeline.py --steps clustering,risk

# Run visualization only (requires previous results)
python scripts/run_full_pipeline.py --steps visualization
```

#### Option 3: Interactive Development
```bash
# Launch exploratory analysis notebook
jupyter notebook notebooks/exploratory_analysis.ipynb

# Or run individual modules for development
cd src/02_iv_estimation
python svi_parameter_estimation.py
```

## 📊 Analysis Pipeline

### 1. **Data Preprocessing** (`src/01_data_preprocessing/`)
- **Files**: `options_data_loader.py`, `summary_statistics.py`
- **Function**: Load raw options data, apply filters, calculate descriptive statistics
- **Outputs**: Cleaned datasets, summary reports

### 2. **Implied Volatility Estimation** (`src/02_iv_estimation/`)
- **Files**: `svi_parameter_estimation.py`, `iv_surface_construction.py`, `interpolation_methods.py`, `daily_iv_processing.py`
- **SVI Model**: Stochastic Volatility Inspired parameterization for each trading day
- **Quality Control**: R² ≥ 0.97 threshold for parameter acceptance
- **Outputs**: SVI parameters, complete IV surfaces, R² statistics

### 3. **Q-Density Estimation** (`src/03_q_density/`)
- **Files**: `q_density_estimation.py`, `density_filtering.py`  
- **Method**: Breeden-Litzenberger formula implementation with R integration
- **Interpolation**: PCHIP (Piecewise Cubic Hermite) for numerical stability
- **Filtering**: Multiple time-to-maturity specifications (5, 9, 14, 27, 45 days)
- **Outputs**: Risk-neutral probability densities

### 4. **Market Regime Clustering** (`src/04_clustering/`)
- **Files**: `market_regime_clustering.py`, `dimensionality_reduction.py`
- **Transformation**: Centered Log-Ratio (CLR) for compositional data
- **Algorithm**: Ward linkage hierarchical clustering 
- **Regime Types**: High-volatility (HV) vs Low-volatility (LV) market states
- **Validation**: Silhouette analysis and stability testing

### 5. **Risk Premium Analysis** (`src/05_risk_analysis/`)
- **Files**: `bitcoin_premium_calculation.py`, `variance_risk_premium.py`, `lower_bounds_analysis.py`, `state_dependent_analysis.py`, `premium_decomposition.py`, `risk_premium_reporting.py`
- **Bitcoin Premium (BP)**: μ_P - μ_Q analysis across return spectrum
- **Variance Risk Premium (VRP)**: Var_Q - Var_P calculations
- **Theoretical Bounds**: Implementation of Chabi-Yo & Loudis (2020) framework
- **Regime Analysis**: State-dependent risk premium behavior

### 6. **Volatility Index** (`src/06_volatility/`)
- **Files**: `bvix_calculation.py`
- **BVIX**: Model-free Bitcoin volatility index following VIX methodology
- **Integration**: Multi-maturity variance swap rate calculation

### 7. **Visualization** (`src/07_visualization/`)
- **Files**: 13 specialized plotting modules including:
  - `iv_surface_plotting.py`: 3D implied volatility surfaces
  - `q_density_plotting.py`: Risk-neutral vs physical density comparisons  
  - `bitcoin_premium_plotting.py`: Risk premium time series and distributions
  - `variance_risk_premium_plotting.py`: VRP analysis and regime comparison
  - `clustering_visualization.py`: PCA/UMAP projections and regime plots
  - `lower_bounds_plotting.py`: Theoretical bounds visualization
- **Output Formats**: High-resolution PDF, PNG, and interactive HTML plots

## ⚙️ Configuration Management

All analysis parameters are centralized in `config/parameters.yaml`:

```yaml
# Time-to-maturity specifications
ttm_values:
  main_analysis: [5, 9, 14, 27, 45]    # Days to expiration
  clustering: [5, 9, 14, 27]           # Subset for regime analysis
  
# SVI model parameters  
svi:
  min_r2_threshold: 0.97               # Minimum R² for acceptance
  max_iterations: 1000                 # Optimization iterations
  parameter_bounds:                    # SVI parameter constraints
    a: [-0.1, 0.1]
    b: [0.01, 1.0]
    rho: [-0.99, 0.99]
    m: [-1.0, 1.0] 
    sigma: [0.01, 2.0]

# Clustering configuration
clustering:
  method: "ward"                       # Linkage method
  height_threshold: 35                 # Dendrogram cut height
  n_clusters: 2                        # Number of regimes
  
# Risk analysis settings
risk_analysis:
  return_bins: 100                     # Return space discretization
  confidence_levels: [0.95, 0.99]     # For confidence intervals
  
# Data filtering
filters:
  min_time_to_maturity: 5              # Minimum days to expiration
  max_time_to_maturity: 45             # Maximum days to expiration
  min_moneyness: 0.8                   # Minimum S/K ratio
  max_moneyness: 1.2                   # Maximum S/K ratio
```

## 📈 Key Research Findings

### Primary Results
1. **Negative returns between -60% and -20% explain 1/3 of Bitcoin equity premium**
2. **Contrasts sharply with S&P 500: moderate negative returns explain 70% of EP**  
3. **Challenges traditional macro-finance models** (habit, disasters, long-run risk)

### Market Regime Analysis
- **Low-Volatility States**: 
  - Primary concern: variance risk
  - U-shaped pricing kernel
  - Symmetric OTM option demand
  
- **High-Volatility States**:
  - Primary concern: downside risk  
  - Asymmetric risk pricing
  - Heightened crash protection demand

### Methodological Contributions
- **Nonparametric approach** avoiding parametric model assumptions
- **CLR transformation** for compositional density data
- **High-frequency regime identification** via hierarchical clustering

## 🛠️ Development & Extension

### Adding New Analysis Modules

1. **Create source file** in appropriate `src/` subdirectory:
   ```python
   # src/05_risk_analysis/new_risk_measure.py
   from src.utils.data_utils import load_processed_data
   from src.utils.config_loader import load_config
   
   def calculate_new_measure(config):
       # Implementation here
       pass
   ```

2. **Update configuration** in `config/parameters.yaml`:
   ```yaml
   new_measure:
     parameter1: value1
     parameter2: value2
   ```

3. **Integrate into pipeline** in `scripts/run_full_pipeline.py`:
   ```python
   if 'new_measure' in steps:
       from src.05_risk_analysis.new_risk_measure import calculate_new_measure
       calculate_new_measure(config)
   ```

4. **Add tests** in `tests/test_new_measure.py`

### Development Workflow

```bash
# Setup development environment
python -m venv btc_env
source btc_env/bin/activate  # On Windows: btc_env\Scripts\activate
pip install -r requirements.txt

# Run code formatting
black src/ scripts/ tests/

# Run linting  
flake8 src/ scripts/ tests/

# Run test suite
python -m pytest tests/ -v

# Run specific test module
python -m pytest tests/test_iv_estimation.py -v
```

### Performance Optimization

- **Parallel Processing**: Utilize `multiprocessing` for daily calculations
- **Memory Management**: Process large datasets in chunks  
- **Caching**: Store intermediate results to avoid recomputation
- **Profiling**: Use `cProfile` for bottleneck identification

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **`methodology.md`**: Detailed mathematical methodology and model specifications
- **`data_description.md`**: Complete data schema and variable definitions  
- **`api_reference.md`**: Function and class documentation
- **`user_guide.md`**: Step-by-step usage examples and troubleshooting
- **`research_notes.md`**: Academic background and literature review

## 🧪 Testing & Validation

```bash
# Run all tests
python -m pytest tests/ -v --cov=src

# Run specific test categories
python -m pytest tests/test_iv_estimation.py -v      # IV model tests
python -m pytest tests/test_clustering.py -v        # Clustering tests  
python -m pytest tests/test_risk_analysis.py -v     # Risk premium tests

# Generate coverage report
python -m pytest tests/ --cov=src --cov-report=html
```

## 📊 Data Requirements

- **Bitcoin Options Data**: Daily options chains (2017-2022)
- **Spot Prices**: Bitcoin price series for moneyness calculations  
- **Interest Rates**: Risk-free rates for options pricing
- **Data Format**: CSV files with columns [Date, Strike, Expiry, OptionType, Price, IV]

## 🔧 Troubleshooting

### Common Issues

1. **R Integration Errors**: Ensure R packages are installed and R is in PATH
2. **Memory Issues**: Use data chunking for large datasets (>1GB)
3. **SVI Convergence**: Adjust parameter bounds in config for difficult fits
4. **Missing Dependencies**: Check `requirements.txt` for all Python packages

### Performance Tips

- Use SSD storage for data directory (faster I/O)
- Increase available RAM for clustering analysis (>8GB recommended)  
- Enable parallel processing in pipeline configuration
- Consider using GPU acceleration for large-scale computations

## 📄 License

This project is licensed under the terms specified in the LICENSE file.

## 🙏 Acknowledgments

Special thanks to:
- Academic institutions supporting this research
- Open-source community for foundational packages
- Bitcoin options data providers
- Research collaborators and reviewers

## 📮 Contact

For questions, collaboration opportunities, or technical support:

- **Research Inquiries**: Contact the authors via institutional email
- **Technical Issues**: Open GitHub issues for bug reports
- **Contributions**: Submit pull requests following contribution guidelines

---

**Last Updated**: December 2024 | **Version**: 2.0 (Post-Reorganization)

