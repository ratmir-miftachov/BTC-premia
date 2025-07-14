


# Main code for: 

# BTC lower bound
# Reference: Chabi-Yo & Loudis (2020), Martin (2017), Foley et al. (2022)

"""
There are three types of lower bound: 
- Martin's lower bound
- Preference-based lower bound (unrestricted) - from Chabi-Yo & Loudis (2020)
- Restricted lower bound - from Chabi-Yo & Loudis (2020)

Notice the preference-based lower bound, there are three parameters in the lower bound formula (27) associated with preference:
- tau
- rho
- kappa

We should estimate these parameters using moment restrictions.

R_M_t - R_f_t = alpha1 + LB1_t + epsilon1
(R_M_t - R_f_t)^2 - M2_t = alpha2 + UB2_t + epsilon2
(R_M_t - R_f_t)^3 - M3_t = alpha3 + LB3_t + epsilon3

"""

import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.optimize import minimize

base_dir = "/Users/irtg/Documents/同步空间/Pricing_Kernel/EPK/SVI_independent_tau/"
os.chdir(base_dir)

ttm = 27
Q_matrix_path = f"Q_matrix/Tau-independent/unique/moneyness_step_0d01/Q_matrix_{ttm}day.csv"
Q_matrix = pd.read_csv(Q_matrix_path)

def moments_Q_density(date_Q, Q_matrix, ttm=27, ret=np.arange(-1, 1.01, 0.01)):
    # date_Q: the date of Q
    # Q_matrix: the first column is the moneyness, the other columns are the dates of the Q densities

    # Read the Q_density of the date_Q
    Q_density = Q_matrix[date_Q]
    Q_density = Q_density.values

    # The return column of Q_matrix
    return_column = Q_matrix['Return']

    # Interpolate the Q-density to map returns we need
    Q_density_interpolated = np.interp(ret, return_column, Q_density, left=0, right=0)

    # Ensure Q-density has no negative values
    if np.any(Q_density_interpolated < 0):
        #print(f"Negative Q-density found for date {date_Q}")
        Q_density_interpolated[Q_density_interpolated < 0] = 0

    # M1: First moment (Mean)
    M1 = np.trapezoid(ret * Q_density_interpolated, ret) 

    # M2: Second moment (Variance)
    M2 = np.trapezoid((ret - M1) ** 2 * Q_density_interpolated, ret) 

    # M3: Third moment (Skewness)
    M3 = np.trapezoid((ret - M1) ** 3 * Q_density_interpolated, ret) #/ M2 ** 1.5

    # M4: Fourth moment (Kurtosis)
    M4 = np.trapezoid((ret - M1) ** 4 * Q_density_interpolated, ret) #/ M2 ** 2

    # M5: Fifth moment
    M5 = np.trapezoid((ret - M1) ** 5 * Q_density_interpolated, ret) 

    # M6: Sixth moment
    M6 = np.trapezoid((ret - M1) ** 6 * Q_density_interpolated, ret) 

    return {'M1': M1, 'M2': M2, 'M3': M3, 'M4': M4, 'M5': M5, 'M6': M6}


def calculate_time_varying_moments(Q_matrix, dates_Q=Q_matrix.columns[1:], ret=np.arange(-1, 1.01, 0.01)):
    M1 = []
    M2 = []
    M3 = []
    M4 = []
    M5 = []
    M6 = []

    for date_Q in dates_Q:

        # Ensure date_Q is in "yyyy-mm-dd" format
        date_Q = pd.to_datetime(date_Q).strftime('%Y-%m-%d')

        # Calculate risk-neutral moments for the given date
        Moments = moments_Q_density(date_Q, Q_matrix, ttm, ret)
        M1_t = Moments['M1']
        M2_t = Moments['M2']
        M3_t = Moments['M3']
        M4_t = Moments['M4']
        M5_t = Moments['M5']
        M6_t = Moments['M6']

        # Store the results
        M1.append((date_Q, M1_t))
        M2.append((date_Q, M2_t))
        M3.append((date_Q, M3_t))
        M4.append((date_Q, M4_t))
        M5.append((date_Q, M5_t))
        M6.append((date_Q, M6_t))

    return {'M1':M1, 'M2':M2, 'M3':M3, 'M4':M4, 'M5':M5, 'M6':M6}

# Load daily price data
BTC_daily_price_path = "Data/BTC_USD_Quandl_2011_2023.csv"
daily_price = pd.read_csv(BTC_daily_price_path, parse_dates=['Date'], dayfirst=False)

# Sort and filter the daily price data
daily_price = daily_price.sort_values(by='Date')
daily_price = daily_price[(daily_price['Date'] <= '2022-12-31') & (daily_price['Date'] >= '2014-01-01')]

# Load the common dates of the multivariate clustering
common_dates_path = "Clustering/Tau-independent/unique/moneyness_step_0d01/multivariate_clustering_9_27_45/common_dates_cluster.csv"
common_dates = pd.read_csv(common_dates_path)

dates_Q = {}
dates_Q[0] = common_dates[common_dates['Cluster']==0]['Date']
dates_Q[1] = common_dates[common_dates['Cluster']==1]['Date']

dates_Q_overall = pd.concat([dates_Q[0], dates_Q[1]])
dates_Q_overall = pd.to_datetime(dates_Q_overall)
dates_Q_overall = dates_Q_overall.sort_values()

# Define the function to calculate forward returns
def return_overall_forward(daily_price, dates_Q_overall, ttm, ret_type="gross"):
    return_forward = []
    for date_Q in dates_Q_overall:

        # Ensure date_Q is datetime
        date_Q = pd.to_datetime(date_Q)

        # Filter the prices for the time period between date_Q and (date_Q + ttm days)
        start_date = date_Q
        end_date = date_Q + pd.Timedelta(days=ttm)
        sp1 = daily_price[(daily_price['Date'] >= start_date) & (daily_price['Date'] <= end_date)]
        sp1 = sp1.sort_values(by='Date')
        
        # Calculate forward return
        if len(sp1) > 0:  # Check if there is enough data for the given period
            if ret_type == "gross":
                forward_return = sp1['Adj.Close'].iloc[-1] / sp1['Adj.Close'].iloc[0]
            elif ret_type == "log":
                forward_return = np.log(sp1['Adj.Close'].iloc[-1] / sp1['Adj.Close'].iloc[0])
            elif ret_type == "simple":
                forward_return = (sp1['Adj.Close'].iloc[-1] / sp1['Adj.Close'].iloc[0]) - 1
            else:
                raise ValueError(f"Invalid return type: {ret_type}")
        else:
            forward_return = np.nan  # Handle missing data
        
        return_forward.append(forward_return)
    
    return np.array(return_forward)

# Calculate forward returns
return_forward = return_overall_forward(daily_price, dates_Q_overall, ttm)

# Define the gross risk-free rate
R_f = 1

# Calculate excess returns (forward return - risk-free rate)
excess_returns = return_forward - R_f

def equation_63(params, Q_matrix, R_f, excess_returns, ret, dates_Q_overall):
    tau, rho, kappa, alpha1, alpha2, alpha3 = params

    params_LB = [tau, rho, kappa]
    
    # Calculate the unrestricted lower bound of expected excess returns
    LB1_t_df = calculate_time_varying_LBU(Q_matrix, params_LB, R_f, dates_Q_overall)
    LB1_t = LB1_t_df['Lower_Bound']

    # Ensure excess_returns_t is numeric
    excess_returns_t = pd.to_numeric(excess_returns, errors='coerce')

    # Compute the residuals for equation (63)
    residuals = excess_returns_t - alpha1 - LB1_t

    return residuals

def equation_64(params, Q_matrix, R_f, excess_returns, ret, dates_Q_overall, Moments):
    tau, rho, kappa, alpha1, alpha2, alpha3 = params

    params_UB = [tau, rho, kappa]
    
    # Calculate the model-implied upper bound of expected excess returns
    UB2_t_df = calculate_time_varying_UBU2(Q_matrix, params_UB, R_f, dates_Q_overall)
    LB2_t = UB2_t_df['Upper_Bound']
    
    # Ensure excess_returns_t is numeric
    excess_returns_t = pd.to_numeric(excess_returns, errors='coerce')
    
    # The 'y' term is defined as excess returns squared minus the second moment (variance)
    M2 = np.array(Moments['M2'])[:,1].astype(float)
    y = excess_returns_t ** 2 - M2
    
    # Compute the residuals for equation (64)
    residuals_64 = y - alpha2 - LB2_t
    
    return residuals_64

def equation_65(params, Q_matrix, R_f, excess_returns, ret, dates_Q_overall, Moments):
    tau, rho, kappa, alpha1, alpha2, alpha3 = params

    params_LB = [tau, rho, kappa]
    
    # Calculate the model-implied lower bound of expected excess returns
    LB3_t_df = calculate_time_varying_LBU3(Q_matrix, params_LB, R_f, dates_Q_overall)
    LB3_t = LB3_t_df['Lower_Bound']
    
    # Ensure excess_returns_t is numeric
    excess_returns_t = pd.to_numeric(excess_returns, errors='coerce')
    
    # The 'y' term is defined as excess returns cubed minus the third moment (M3)
    M3 = np.array(Moments['M3'])[:,1].astype(float)
    y = excess_returns_t ** 3 - M3
    
    # Compute the residuals for equation (65)
    residuals = y - alpha3 - LB3_t
    
    return residuals

def calculate_time_varying_LBR(Q_matrix, R_f, dates_Q_overall=Q_matrix.columns[1:], ret=np.arange(-1, 1.01, 0.01)):

    # LBR: restricted lower bound

    # This follows Eq. (31) in Chabi-Yo & Loudis (2020)

    LBR1s = []

    for date_Q in dates_Q_overall:

        # Ensure date_Q is in "yyyy-mm-dd" format
        date_Q = pd.to_datetime(date_Q).strftime('%Y-%m-%d')

        # Calculate risk-neutral moments for the given date
        Moments = moments_Q_density(date_Q, Q_matrix, ttm=ttm, ret=ret)
        M_2 = Moments['M2']
        M_3 = Moments['M3']
        M_4 = Moments['M4']

        # Compute restricted lower bound using equation (31) in Chabi-Yo & Loudis (2020)
        numerator = M_2/R_f - M_3/R_f**2 + M_4/R_f**3
        denominator = 1 - M_2/R_f**2 + M_3/R_f**3

        # Calculate lower bound for the given date
        LB1_t = numerator / denominator

        # Store the result
        LBR1s.append((date_Q, LB1_t))

    # Convert to a DataFrame for better handling
    LBR1_df = pd.DataFrame(LBR1s, columns=['Date', 'Lower_Bound'])

    return LBR1_df

def calculate_time_varying_LBU(Q_matrix, params, R_f, dates_Q_overall=Q_matrix.columns[1:], ret=np.arange(-1, 1.01, 0.01)):

    lower_bounds = []

    tau, rho, kappa = params

    for date_Q in dates_Q_overall:

        # Ensure date_Q is in "yyyy-mm-dd" format
        date_Q = pd.to_datetime(date_Q).strftime('%Y-%m-%d')

        # Calculate risk-neutral moments for the given date
        Moments = moments_Q_density(date_Q, Q_matrix, ttm=ttm, ret=ret)
        M_2 = Moments['M2']
        M_3 = Moments['M3']
        M_4 = Moments['M4']

        # Compute theta parameters using equation (21) in Chabi-Yo & Loudis (2020)
        theta_1 = 1 / (tau * R_f)
        theta_2 = (1 - rho) / (tau ** 2 * R_f ** 2)
        theta_3 = (1 - 2 * rho + kappa) / (tau ** 3 * R_f ** 3)

        # Estimate the lower bound using equation (27) in Chabi-Yo & Loudis (2020)
        numerator = theta_1 * M_2 + theta_2 * M_3 + theta_3 * M_4
        denominator = 1 + theta_2 * M_2 + theta_3 * M_3

        # Calculate lower bound for the given date
        LB1_t = numerator / denominator

        # Store the result
        lower_bounds.append((date_Q, LB1_t))

    # Convert to a DataFrame for better handling
    LBU = pd.DataFrame(lower_bounds, columns=['Date', 'Lower_Bound'])

    return LBU

def calculate_time_varying_UBU2(Q_matrix, params, R_f, dates_Q_overall=Q_matrix.columns[1:], ret=np.arange(-1, 1.01, 0.01)):

    upper_bounds = []

    tau, rho, kappa = params

    for date_Q in dates_Q_overall:

        # Ensure date_Q is in "yyyy-mm-dd" format
        date_Q = pd.to_datetime(date_Q).strftime('%Y-%m-%d')

        # Calculate risk-neutral moments for the given date
        Moments = moments_Q_density(date_Q, Q_matrix, ttm=ttm, ret=ret)
        M1 = Moments['M1']
        M2 = Moments['M2']
        M3 = Moments['M3']
        M4 = Moments['M4']
        M5 = Moments['M5']

        # Compute theta parameters using equation (21) in Chabi-Yo & Loudis (2020)
        theta_1 = 1 / (tau * R_f)
        theta_2 = (1 - rho) / (tau ** 2 * R_f ** 2)
        theta_3 = (1 - 2 * rho + kappa) / (tau ** 3 * R_f ** 3)

        # Estimate the lower bound using equation (27) in Chabi-Yo & Loudis (2020)
        numerator = theta_1 * M3 + theta_2 * (M4 - M2 ** 2) + theta_3 * (M5 - M3 * M2)
        denominator = 1 + theta_2 * M2 + theta_3 * M3

        # Calculate lower bound for the given date
        UB2_t = numerator / denominator

        # Store the result
        upper_bounds.append((date_Q, UB2_t))

    # Convert to a DataFrame for better handling
    UBU2 = pd.DataFrame(upper_bounds, columns=['Date', 'Upper_Bound'])

    return UBU2

def calculate_time_varying_LBU3(Q_matrix, params, R_f, dates_Q_overall=Q_matrix.columns[1:], ret=np.arange(-1, 1.01, 0.01)):

    lower_bounds = []

    tau, rho, kappa = params

    for date_Q in dates_Q_overall:

        # Ensure date_Q is in "yyyy-mm-dd" format
        date_Q = pd.to_datetime(date_Q).strftime('%Y-%m-%d')

        # Calculate risk-neutral moments for the given date
        Moments = moments_Q_density(date_Q, Q_matrix, ttm=ttm, ret=ret)
        M2 = Moments['M2']
        M3 = Moments['M3']
        M4 = Moments['M4']
        M5 = Moments['M5']
        M6 = Moments['M6']

        # Compute theta parameters using equation (21) in Chabi-Yo & Loudis (2020)
        theta_1 = 1 / (tau * R_f)
        theta_2 = (1 - rho) / (tau ** 2 * R_f ** 2)
        theta_3 = (1 - 2 * rho + kappa) / (tau ** 3 * R_f ** 3)

        # Estimate the lower bound using equation (27) in Chabi-Yo & Loudis (2020)
        numerator = theta_1 * M4 + theta_2 * (M5 - M3 * M2) + theta_3 * (M6 - M3 ** 2)
        denominator = 1 + theta_2 * M2 + theta_3 * M3

        # Calculate lower bound for the given date
        LB3_t = numerator / denominator

        # Store the result
        lower_bounds.append((date_Q, LB3_t))

    # Convert to a DataFrame for better handling
    LBU3 = pd.DataFrame(lower_bounds, columns=['Date', 'Lower_Bound'])

    return LBU3

def estimate_preference_parameters_in_LBU(Q_matrix, params0, R_f, excess_returns, Moments, ret=np.arange(-1, 1.01, 0.01), \
    dates_Q_overall=Q_matrix.columns[1:]):

    # First step: equally weighted moments for Eq. (63)-(65)
    # Nonlinear least squares
    # Define the objective function
    def objective_function(params, weights, Q_matrix, R_f, ret=np.arange(-1, 1.01, 0.01), \
        dates_Q_overall=Q_matrix.columns[1:]):

        weight63 = weights[0]
        weight64 = weights[1]
        weight65 = weights[2]

        tau, rho, kappa, alpha1, alpha2, alpha3 = params
        params_LBU = [tau, rho, kappa]
        
        # Calculate the lower bound
        LBU = calculate_time_varying_LBU(Q_matrix, params_LBU, R_f, dates_Q_overall, ret)

        residual63 = equation_63(params, Q_matrix, R_f, excess_returns, ret, dates_Q_overall)
        residual64 = equation_64(params, Q_matrix, R_f, excess_returns, ret, dates_Q_overall, Moments)
        residual65 = equation_65(params, Q_matrix, R_f, excess_returns, ret, dates_Q_overall, Moments)

        return np.sum(residual63 ** 2 * weight63 + residual64 **2 * weight64 + residual65 ** 2 * weight65)
    
    # Equal weights
    weights = [w/3 for w in [1, 1, 1]]

    # Use scipy.optimize.minimize to find the optimal parameters
    result = minimize(objective_function, params0, args=(weights, Q_matrix, R_f, ret, dates_Q_overall), method='Nelder-Mead')

    # Extract the optimized parameters
    params = result.x

    fitness = result.fun
    print(f"The fitness of the first step is {fitness}")

    residual63 = equation_63(params, Q_matrix, R_f, excess_returns, ret, dates_Q_overall)
    residual64 = equation_64(params, Q_matrix, R_f, excess_returns, ret, dates_Q_overall, Moments)
    residual65 = equation_65(params, Q_matrix, R_f, excess_returns, ret, dates_Q_overall, Moments)

    Variance63 = np.var(residual63)
    Variance64 = np.var(residual64)
    Variance65 = np.var(residual65)

    weights_new = [1 / Variance63, 1 / Variance64, 1 / Variance65]
    weights_new = weights_new / np.sum(weights_new)

    # Second step: weighted by variance of residuals s.t. more weights for lower variance
    result_2nd = minimize(objective_function, params, args=(weights_new, Q_matrix, R_f, ret, dates_Q_overall), method='Nelder-Mead')
    params = result_2nd.x

    fitness = result_2nd.fun
    print(f"The fitness of the second step is {fitness}")
    
    return params

# The gross risk-free rate, set to 1 because it is defined by simple return plus one
R_f = 1

# Calculate time-varying moments
Moments = calculate_time_varying_moments(Q_matrix, dates_Q_overall)

# Convert Moments to numpy arrays for element-wise operations
M2_array = np.array(Moments['M2'])[:,1].astype(float)
M3_array = np.array(Moments['M3'])[:,1].astype(float)
M4_array = np.array(Moments['M4'])[:,1].astype(float)

# Estimate params using two-step nonlinear least squares 
# Set initial values for the parameters
tau = 0.97 # risk tolerance
rho = 2.32 # skewness preference
kappa = 3.50 # kurtosis preference
alpha1 = 0.0042
alpha2 = -1e-4
alpha3 = 9.2e-5

params = [tau, rho, kappa, alpha1, alpha2, alpha3]
weights = [w/3 for w in [1, 1, 1]]
params_estimated = estimate_preference_parameters_in_LBU(Q_matrix, params, R_f, excess_returns, 
                                               Moments,
                                               np.arange(-1, 1.01, 0.01),
                                               dates_Q_overall)

tau = params_estimated[0]
rho = params_estimated[1]
kappa = params_estimated[2]
params = [tau, rho, kappa]
    
# Calculate the unrestricted lower bounds using Eq. (27) in Chabi-Yo & Loudis (2020)
LBU = calculate_time_varying_LBU(Q_matrix, params, R_f, dates_Q_overall)
LBU["Lower_Bound"] = LBU["Lower_Bound"] / ttm * 365

# Calculate the restricted lower bounds using Eq. (31) in Chabi-Yo & Loudis (2020)
LBR = calculate_time_varying_LBR(Q_matrix, R_f, dates_Q_overall) # LBR is already df

# Martin (2017) measure of lower bound
# Section 2.3 in Chabi-Yo & Loudis (2020) illustrates the formula
MB = {'Lower_Bound': M2_array / R_f /ttm * 365, 'Date': dates_Q_overall}
MB = pd.DataFrame(MB, columns=['Date', 'Lower_Bound'])

# Chabi-Yo & Loudis (2020) restricted lower bound
# Equation (31) LBR

numerator = M2_array / R_f - M3_array / R_f**2 + M4_array / R_f**3
denominator = 1 - M2_array / R_f**2 + M3_array / R_f**3
LBR = {'Lower_Bound':  numerator / denominator /ttm * 365, 'Date': dates_Q_overall}
LBR = pd.DataFrame(LBR, columns=['Date', 'Lower_Bound'])

# Plot
# Ensure both Date columns are in datetime format
MB['Date'] = pd.to_datetime(MB['Date'])
LBU['Date'] = pd.to_datetime(LBU['Date'])
LBR['Date'] = pd.to_datetime(LBR['Date'])

# Create the plot
plt.figure(figsize=(10, 6))

# Plot Martin (2017) lower bounds
plt.plot(MB['Date'], MB['Lower_Bound'], label='Martin (2017) Lower Bound', color='red', linewidth=2)

# Plot Chabi-Yo & Loudis (2020) Unrestricted Lower Bound
plt.plot(LBU['Date'], LBU['Lower_Bound'], label='Chabi-Yo & Loudis (2020) Unrestricted Lower Bound', color='blue', linewidth=2)

# Plot Chabi-Yo & Loudis (2020) Restricted Lower Bound
plt.plot(LBR['Date'], LBR['Lower_Bound'], label='Chabi-Yo & Loudis (2020) Restricted Lower Bound', color='green', linewidth=2)

# Formatting the x-axis with yearly intervals and specific date limits
plt.gca().xaxis.set_major_locator(mdates.YearLocator())  # Set major ticks to yearly intervals
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  # Set the date format to just show the year

# Convert date limits to the appropriate datetime format
start_date = pd.to_datetime('2017-07-01')
end_date = pd.to_datetime('2022-12-17')

# Set limits for the x-axis
plt.xlim(start_date, end_date)

# Add labels and title
plt.xlabel('Date', fontsize=18)
plt.ylabel('Lower Bound', fontsize=18)
plt.title('Time-Varying Lower Bound of Bitcoin Premium (BP)', fontsize=18)

# Rotate x-tick labels for better readability
plt.xticks(rotation=45)

# Add grid, legend, and show the plot
plt.grid(True)
plt.tight_layout()
plt.legend(fontsize=12)

# Save the plot
lower_bound_plot_path = "Lower_Bound/Tau-independent/unique/moneyness_step_0d01/multivariate_clustering_9_27_45/Martin_Chabi-Yo_RLB_Preference_LB.png"
os.makedirs(os.path.dirname(lower_bound_plot_path), exist_ok=True)
plt.savefig(lower_bound_plot_path, dpi=300, bbox_inches='tight')

# Show the plot
plt.show()

# Save the lower bounds in csv
MB.to_csv("Lower_Bound/Tau-independent/unique/moneyness_step_0d01/multivariate_clustering_9_27_45/Martin_LB.csv", index=False)
LBU.to_csv("Lower_Bound/Tau-independent/unique/moneyness_step_0d01/multivariate_clustering_9_27_45/Chabi-Yo_ULB.csv", index=False)
LBR.to_csv("Lower_Bound/Tau-independent/unique/moneyness_step_0d01/multivariate_clustering_9_27_45/Chabi-Yo_RLB.csv", index=False)

# Show the details of lower bounds
print(f"Q first moment: {np.average(np.array(Moments['M1'])[:,1].astype(float))}")
print(f"Q variance: {np.average(M2_array)}")
print(f"Skewness: {np.average(M3_array)} std. {np.std(M3_array)}")
print(f"Kurtosis: {np.average(M4_array)} std. {np.std(M4_array)}")
print(f"Martin (2017) lower bound: {np.average(MB['Lower_Bound'])}")
print(f"Chabi-Yo & Loudis (2020) unrestricted lower bound: {np.average(LBU['Lower_Bound'])}")
print(f"Chabi-Yo & Loudis (2020) restricted lower bound: {np.average(LBR['Lower_Bound'])}")


print(f"For unrestricted lower bound")
theta1 = 1/(tau*R_f)
theta2 = (1-rho)/(tau**2 * R_f **2)
theta3 = (1-2*rho+kappa)/(tau**3*R_f**3)
print(f"theta1: {theta1}, theta2: {theta2}, theta3: {theta3}")
print(f"the numerator is theta1 * M2 + theta2 * M3 + theta3 * M4")
print(f"{np.average(theta1*M2_array + theta2*M3_array + theta3*M4_array)}")
print(f"the denominator is 1 + theta2 * M2 + theta3 * M3")
print(f"{np.average(1 + theta2*M2_array + theta3*M3_array)}")

print(f"For restricted lower bound")
print(f"the numerator is M2/R_f - M3/R_f**2 + M4/R_f**3")
print(f"{np.average(M2_array/R_f - M3_array/R_f**2 + M4_array/R_f**3)}")
print(f"the denominator is 1 - M2/R_f**2 + M3/R_f**3")
print(f"{np.average(1-M2_array/R_f**2 + M3_array/R_f**3)}")

# Lower bounds for the two clusters: HV and LV
dates_HV = pd.to_datetime(dates_Q[0])
dates_LV = pd.to_datetime(dates_Q[1])

# HV Lower Bounds
LBU_HV = LBU[LBU['Date'].isin(dates_HV)]
LBR_HV = LBR[LBR['Date'].isin(dates_HV)]
MB_HV = MB[MB['Date'].isin(dates_HV)]

# LV Lower Bounds
LBU_LV = LBU[LBU['Date'].isin(dates_LV)]
LBR_LV = LBR[LBR['Date'].isin(dates_LV)]
MB_LV = MB[MB['Date'].isin(dates_LV)]

summary_df = pd.DataFrame({
    'Metric': ['Mean', 'Median', 'Std'],
    'LBU_HV': [LBU_HV['Lower_Bound'].mean(), LBU_HV['Lower_Bound'].median(), LBU_HV['Lower_Bound'].std()],
    'LBU_LV': [LBU_LV['Lower_Bound'].mean(), LBU_LV['Lower_Bound'].median(), LBU_LV['Lower_Bound'].std()],
    'LBR_HV': [LBR_HV['Lower_Bound'].mean(), LBR_HV['Lower_Bound'].median(), LBR_HV['Lower_Bound'].std()],
    'LBR_LV': [LBR_LV['Lower_Bound'].mean(), LBR_LV['Lower_Bound'].median(), LBR_LV['Lower_Bound'].std()],
    'MB_HV': [MB_HV['Lower_Bound'].mean(), MB_HV['Lower_Bound'].median(), MB_HV['Lower_Bound'].std()],
    'MB_LV': [MB_LV['Lower_Bound'].mean(), MB_LV['Lower_Bound'].median(), MB_LV['Lower_Bound'].std()],
})

print(summary_df)

