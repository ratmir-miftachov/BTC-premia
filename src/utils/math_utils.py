"""
Mathematical Utilities for BTC-Premia Analysis

Common mathematical and financial functions used across the project.
"""

import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator
from scipy.stats.mstats import gmean
from typing import Tuple, Optional


def svi_model(theta: np.ndarray, k: np.ndarray, tau: float) -> np.ndarray:
    """
    SVI (Stochastic Volatility Inspired) model for implied volatility.
    
    Parameters:
    -----------
    theta : array-like
        SVI parameters [a, b, rho, m, sigma, a_ttm, b_ttm, rho_ttm, m_ttm, sigma_ttm]
    k : array-like
        Log-moneyness values
    tau : float
        Time to maturity
    
    Returns:
    --------
    array-like
        SVI model values
    """
    base_params = np.array(theta[:5])
    ttm_coeffs = np.array(theta[5:])
    a, b, rho, m, sigma = base_params + ttm_coeffs * tau
    return a + b * (rho * (k - m) + np.sqrt((k - m) ** 2 + sigma ** 2))


def clr_transform(x: np.ndarray) -> np.ndarray:
    """
    Centered Log-Ratio (CLR) transformation for compositional data.
    
    Parameters:
    -----------
    x : array-like
        Input data
    
    Returns:
    --------
    array-like
        CLR transformed data: log(x) - log(gmean(x))
    """
    return np.log(x) - np.log(gmean(x))


def compute_iv_derivatives(iv: np.ndarray, log_ret: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute first and second derivatives of IV with respect to log returns.
    
    Parameters:
    -----------
    iv : array-like
        Implied volatility values
    log_ret : array-like
        Log return values
    
    Returns:
    --------
    tuple
        (first_derivative, second_derivative)
    """
    # First derivative using central differences
    div_dr = np.zeros_like(iv)
    div_dr[1:-1] = (iv[2:] - iv[:-2]) / (log_ret[2:] - log_ret[:-2])
    div_dr[0] = (iv[1] - iv[0]) / (log_ret[1] - log_ret[0])
    div_dr[-1] = (iv[-1] - iv[-2]) / (log_ret[-1] - log_ret[-2])
    
    # Second derivative using central differences
    d2iv_dr2 = np.zeros_like(iv)
    d2iv_dr2[1:-1] = (iv[2:] - 2 * iv[1:-1] + iv[:-2]) / ((log_ret[2:] - log_ret[:-2]) ** 2)
    d2iv_dr2[0] = (iv[2] - 2 * iv[1] + iv[0]) / ((log_ret[1] - log_ret[0]) ** 2)
    d2iv_dr2[-1] = (iv[-1] - 2 * iv[-2] + iv[-3]) / ((log_ret[-1] - log_ret[-2]) ** 2)
    
    return div_dr, d2iv_dr2


def compute_density_moments(ret: np.ndarray, density: np.ndarray, ttm: int) -> dict:
    """
    Compute the first six moments of a density function.
    
    Parameters:
    -----------
    ret : array-like
        Return grid
    density : array-like
        Density values
    ttm : int
        Time to maturity in days
    
    Returns:
    --------
    dict
        Dictionary with moments M1-M6, scaled by 365/ttm
    """
    # Compute raw moments
    m1 = np.trapezoid(density * ret, ret)
    m2 = np.trapezoid(density * (ret - m1)**2, ret)
    m3 = np.trapezoid(density * (ret - m1)**3, ret)
    m4 = np.trapezoid(density * (ret - m1)**4, ret)
    m5 = np.trapezoid(density * (ret - m1)**5, ret)
    m6 = np.trapezoid(density * (ret - m1)**6, ret)
    
    # Scale by annualization factor
    scaling = 365 / ttm
    
    return {
        'M1': m1 * scaling,
        'M2': m2 * scaling,
        'M3': m3 * scaling,
        'M4': m4 * scaling,
        'M5': m5 * scaling,
        'M6': m6 * scaling
    }


def interpolate_density(returns: np.ndarray, density: np.ndarray, 
                       new_returns: np.ndarray, 
                       method: str = 'pchip') -> np.ndarray:
    """
    Interpolate density function to new return grid.
    
    Parameters:
    -----------
    returns : array-like
        Original return grid
    density : array-like
        Original density values
    new_returns : array-like
        New return grid for interpolation
    method : str
        Interpolation method ('pchip', 'linear')
    
    Returns:
    --------
    array-like
        Interpolated density values
    """
    if method.lower() == 'pchip':
        interp_func = PchipInterpolator(returns, density, extrapolate=False)
        interpolated = interp_func(new_returns)
        # Set extrapolated values to 0
        interpolated[np.isnan(interpolated)] = 0
    else:
        interpolated = np.interp(new_returns, returns, density, left=0, right=0)
    
    return interpolated


def normalize_density(density: np.ndarray, returns: np.ndarray) -> np.ndarray:
    """
    Normalize density to integrate to 1.
    
    Parameters:
    -----------
    density : array-like
        Density values
    returns : array-like
        Return grid
    
    Returns:
    --------
    array-like
        Normalized density
    """
    integral = np.trapezoid(density, returns)
    if integral > 0:
        return density / integral
    else:
        return density


def calculate_bitcoin_premium(ret: np.ndarray, 
                             p_density: np.ndarray, 
                             q_density: np.ndarray, 
                             ttm: int,
                             risk_free_rate: float = 0.0) -> float:
    """
    Calculate Bitcoin Premium (BP) as difference between P and Q expected returns.
    
    Parameters:
    -----------
    ret : array-like
        Return grid
    p_density : array-like
        Physical density
    q_density : array-like
        Risk-neutral density
    ttm : int
        Time to maturity in days
    risk_free_rate : float
        Risk-free rate (annualized)
    
    Returns:
    --------
    float
        Bitcoin premium (annualized)
    """
    # Expected returns under P and Q measures
    e_p = np.trapezoid(ret * p_density, ret)
    e_q = np.trapezoid(ret * q_density, ret) if q_density is not None else risk_free_rate * ttm / 365
    
    # Annualize
    bp = (e_p - e_q) * 365 / ttm
    
    return bp


def calculate_variance_risk_premium(ret: np.ndarray, 
                                  p_density: np.ndarray, 
                                  q_density: np.ndarray, 
                                  ttm: int) -> float:
    """
    Calculate Variance Risk Premium (VRP) as difference between Q and P variances.
    
    Parameters:
    -----------
    ret : array-like
        Return grid
    p_density : array-like
        Physical density
    q_density : array-like
        Risk-neutral density
    ttm : int
        Time to maturity in days
    
    Returns:
    --------
    float
        Variance risk premium (annualized)
    """
    # Expected returns
    e_p = np.trapezoid(ret * p_density, ret)
    e_q = np.trapezoid(ret * q_density, ret)
    
    # Variances
    var_p = np.trapezoid((ret - e_p)**2 * p_density, ret)
    var_q = np.trapezoid((ret - e_q)**2 * q_density, ret)
    
    # VRP (annualized)
    vrp = (var_q - var_p) * 365 / ttm
    
    return vrp


def check_svi_constraints(theta: np.ndarray, ttm_values: np.ndarray) -> bool:
    """
    Check if SVI parameters satisfy no-arbitrage constraints.
    
    Parameters:
    -----------
    theta : array-like
        SVI parameters
    ttm_values : array-like
        Time to maturity values to check
    
    Returns:
    --------
    bool
        True if constraints are satisfied
    """
    base_params = np.array(theta[:5])
    ttm_coeffs = np.array(theta[5:])
    
    for ttm in ttm_values:
        a, b, rho, m, sigma = base_params + ttm_coeffs * ttm
        
        # Check constraints
        if b <= 0:  # b > 0
            return False
        if abs(rho) >= 1:  # |rho| < 1
            return False
        if sigma <= 0:  # sigma > 0
            return False
        if a + b * sigma * np.sqrt(1 - rho**2) <= 0:  # no calendar arbitrage
            return False
    
    return True 