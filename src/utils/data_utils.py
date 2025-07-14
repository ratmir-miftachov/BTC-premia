"""
Data Utilities for BTC-Premia Analysis

Common data processing functions used across the project.
"""

import os
import pandas as pd
import numpy as np
from typing import List, Tuple, Optional, Union
from pathlib import Path


def load_btc_data(file_path: str) -> pd.DataFrame:
    """Load and basic preprocessing of BTC data."""
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    return df


def filter_option_data(df: pd.DataFrame, 
                      min_price: float = 10.0,
                      min_btc_price: float = 1500.0,
                      min_tau: float = 0.0) -> pd.DataFrame:
    """Filter option data based on standard criteria."""
    # Remove options with IV <= 0
    df = df[df['IV'] > 0]
    
    # Remove options with tau <= 0
    df = df[df['tau'] > min_tau]
    
    # Remove options with price < min_price
    df = df[df['option_price'] > min_price]
    
    # Remove observations with extremely low BTC price
    df = df[df['BTC_price'] >= min_btc_price]
    
    return df


def calculate_moneyness(df: pd.DataFrame, 
                       moneyness_type: str = 'log') -> pd.DataFrame:
    """Calculate moneyness from strike and underlying price."""
    if moneyness_type == 'log':
        df['moneyness'] = np.log(df['K'] / df['BTC_price'])
    elif moneyness_type == 'simple':
        df['moneyness'] = df['K'] / df['BTC_price'] - 1
    else:
        raise ValueError("moneyness_type must be 'log' or 'simple'")
    
    return df


def load_iv_matrix(file_path: str) -> pd.DataFrame:
    """Load IV matrix from CSV file with error handling."""
    try:
        df = pd.read_csv(file_path)
        
        # Check for NaN values
        if df.isna().any().any():
            print(f"Warning: {file_path} contains NaN values")
            return None
            
        # Check minimum number of columns (at least 3 TTMs)
        if len(df.columns) <= 3:
            print(f"Warning: {file_path} has insufficient columns ({len(df.columns)})")
            return None
            
        return df
        
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None


def extract_date_from_filename(filename: str) -> Optional[str]:
    """Extract date from filename in various formats."""
    import re
    
    # Try different date patterns
    patterns = [
        r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
        r'(\d{8})',              # YYYYMMDD
        r'(\d{4}_\d{2}_\d{2})',  # YYYY_MM_DD
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            date_str = match.group(1)
            # Normalize to YYYY-MM-DD format
            if len(date_str) == 8:  # YYYYMMDD
                return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            elif '_' in date_str:  # YYYY_MM_DD
                return date_str.replace('_', '-')
            else:
                return date_str
    
    return None


def get_common_dates(*dataframes: pd.DataFrame, date_col: str = 'Date') -> List[str]:
    """Find common dates across multiple dataframes."""
    if not dataframes:
        return []
    
    common_dates = set(dataframes[0][date_col])
    for df in dataframes[1:]:
        common_dates = common_dates.intersection(set(df[date_col]))
    
    return sorted(list(common_dates))


def create_return_grid(min_ret: float = -1.0, 
                      max_ret: float = 1.0, 
                      step: float = 0.01) -> np.ndarray:
    """Create standard return grid for analysis."""
    return np.arange(min_ret, max_ret + step, step)


def save_results(data: Union[pd.DataFrame, dict], 
                output_path: str, 
                file_format: str = 'csv') -> None:
    """Save results in specified format."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    if file_format.lower() == 'csv':
        if isinstance(data, pd.DataFrame):
            data.to_csv(output_path, index=False)
        else:
            pd.DataFrame(data).to_csv(output_path, index=False)
    elif file_format.lower() == 'pickle':
        pd.to_pickle(data, output_path)
    else:
        raise ValueError(f"Unsupported format: {file_format}")


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    import yaml
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


class DataPaths:
    """Centralized data path management."""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        
    @property
    def data_dir(self) -> Path:
        return self.base_path / "data"
        
    @property
    def iv_surfaces_dir(self) -> Path:
        return self.data_dir / "iv_surfaces"
        
    @property
    def q_densities_dir(self) -> Path:
        return self.data_dir / "q_densities"
        
    @property
    def clusters_dir(self) -> Path:
        return self.data_dir / "clusters"
        
    @property
    def risk_premia_dir(self) -> Path:
        return self.data_dir / "risk_premia"
        
    @property
    def results_dir(self) -> Path:
        return self.base_path / "results"
        
    @property
    def figures_dir(self) -> Path:
        return self.results_dir / "figures" 