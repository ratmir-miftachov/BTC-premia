import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from statsmodels.nonparametric.smoothers_lowess import lowess
from mpl_toolkits.mplot3d import Axes3D

# Initialize a list to save results
results_list = []
thetas_dict = {}

# Set some Local Folder path
plots_folder = "/home/RDC/miftachr/H:/miftachr/SVI"
if not os.path.exists(plots_folder):
    os.makedirs(plots_folder)

def process_csv_file(filename):
    import os
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.optimize import minimize
    from statsmodels.nonparametric.smoothers_lowess import lowess
    from mpl_toolkits.mplot3d import Axes3D

    # read data:
    df = pd.read_csv(filename)

    if df.isna().any().any():
        print(f"Skipping {filename} because it contains 'NaN' values.")
        return

    #at least 3 ttms observed
    if len(df.columns) <= 3:
        print(f"Skipping {filename} due to having {len(df.columns)} columns.")
        return

    df = df.transpose()

    # Filter out non-numeric indices and convert to integers
    filtered_indices = [int(i) for i in df.index if i.isnumeric()]
    # Convert the list of integers to a numpy array
    row_names_array = np.array(filtered_indices)

    iv_real = df.iloc[1:, :]
    iv = iv_real.to_numpy()

    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.optimize import minimize
    from statsmodels.nonparametric.smoothers_lowess import lowess
    from mpl_toolkits.mplot3d import Axes3D

    # SVI model with ttm dependence
    def svi_model(theta, k, tau):
        base_params = np.array(theta[:5])
        ttm_coeffs = np.array(theta[5:])
        a, b, rho, m, sigma = base_params + ttm_coeffs * tau
        return a + b * (rho * (k - m) + np.sqrt((k - m) ** 2 + sigma ** 2))

    def objective_function_grid(theta, k_grid, tau_grid, iv_obs_grid):
        # Specify the ttm of interest, e.g. 5, 9, 14 or 27
        iv_obs_grid = iv_obs_grid.reshape(tau_grid.shape[0], k_grid.shape[1])
        iv_model_grid = np.empty_like(iv_obs_grid)

        penalty = 0
        epsilon = 1e-10
        for i in range(tau_grid.shape[0]):
            for j in range(k_grid.shape[1]):
                iv_model_val = svi_model(theta, k_grid[i, j], tau_grid[i, j]) / tau_grid[i, j]

                if iv_model_val < -epsilon:
                    penalty += 100000  # Large value. Don't change.
                    iv_model_grid[i, j] = 0
                else:
                    iv_model_grid[i, j] = np.sqrt(max(iv_model_val, 0))

        mse = np.mean((iv_model_grid - iv_obs_grid) ** 2)
        return np.sqrt(mse) + penalty

    # Given data
    ttm = row_names_array
    # ttm of interest, e.g. 5, 9 , 14 or 27
    ttm_of_interest = 5
    k = df.iloc[0, :].to_numpy()

    # Generate a grid of strike prices for interpolation
    k_new = np.linspace(k.min(), k.max(), 100)  # Grid of log moneyness

    # Interpolate IVs at new strike prices for each ttm
    iv_new = np.empty((len(ttm), len(k_new)))
    for i in range(len(ttm)):
        smoothed = lowess(iv[i, :], k, frac=0.3)  # use local polynomial regression
        iv_new[i, :] = np.interp(k_new, smoothed[:, 0], smoothed[:, 1])

    # Linearly interpolate IVs at ttm=7 for each strike price with weights
    iv_at_9_weighted = np.empty(len(k_new))
    for i in range(len(k_new)):
        # Calculate weights
        weights = 1 / np.abs(ttm - ttm_of_interest)
        weights = weights / np.sum(weights)

        # Calculate weighted average
        iv_at_9_weighted[i] = np.average(iv_new[:, i], weights=weights)

    def callback(theta):
        loss = objective_function_grid(theta, k_grid, ttm_grid, iv.ravel())
        print('Loss at current iteration:', loss)

    # Create grid for optimization
    k_grid, ttm_grid = np.meshgrid(k_new, ttm)

    # Define SVI constraints
    def constraint1(theta):
        base_params = np.array(theta[:5])
        ttm_coeffs = np.array(theta[5:])
        values = [base_params[1] + ttm_coeffs[1] * t for t in ttm]
        if any(np.isnan(values)):
            return -1e10
        return min(values)

    def constraint2(theta):
        base_params = np.array(theta[:5])
        ttm_coeffs = np.array(theta[5:])
        values = [1 - abs(base_params[2] + ttm_coeffs[2] * t) for t in ttm]
        if any(np.isnan(values)):
            return -1e10
        return min(values)

    def constraint3(theta):
        base_params = np.array(theta[:5])
        ttm_coeffs = np.array(theta[5:])
        values = [base_params[0] + ttm_coeffs[0] * t + (base_params[1] + ttm_coeffs[1] * t) * (
                    base_params[4] + ttm_coeffs[4] * t) * np.sqrt(1 - (base_params[2] + ttm_coeffs[2] * t) ** 2) for t
                  in ttm]
        if any(np.isnan(values)):
            return -1e10
        return min(values)

    def constraint4(theta):
        base_params = np.array(theta[:5])
        ttm_coeffs = np.array(theta[5:])
        values = [base_params[4] + ttm_coeffs[4] * t for t in ttm]
        if any(np.isnan(values)):
            return -1e10
        return min(values)

    # Create the constraints dictionary
    constraints = [{'type': 'ineq', 'fun': constraint1},
                   {'type': 'ineq', 'fun': constraint2},
                   {'type': 'ineq', 'fun': constraint3},
                   {'type': 'ineq', 'fun': constraint4}]

    # Initialization
    theta_guess = 0.05 * np.random.rand(10)
    max_iterations = 4  # set some max number of iterations to avoid infinite loops
    iteration_count = 0
    # bounds for 10 parameters. Do not change!
    bounds = [(-4, 4), (-50, 18), (-2, 2), (-2, 2), (-0.5, 1), (-50, 50), (-50, 50), (-2, 2), (-2, 2), (-2, 0.5)]
    lower_bounds = np.array([bound[0] for bound in bounds])
    upper_bounds = np.array([bound[1] for bound in bounds])

    while iteration_count < max_iterations:
        iteration_count += 1

        optimized_thetas = []
        losses = []

        # Iterative Optimization
        for _ in range(10):
            # Vectorized check if thetas are within bounds. If not, set to 0.
            out_of_bounds = (theta_guess < lower_bounds) | (theta_guess > upper_bounds)
            theta_guess[out_of_bounds] = 0

            result = minimize(objective_function_grid, theta_guess, args=(k_grid, ttm_grid, iv.ravel()),
                              constraints=constraints, method='SLSQP', bounds=bounds)

            optimized_thetas.append(result.x)
            losses.append(result.fun)  # Assuming result.fun contains the final loss, adjust if not

            # Update the theta_guess for the next iteration
            theta_guess = result.x + 0.02 * np.random.rand(10)

        # Review Results
        best_iteration = np.argmin(losses)
        best_thetas = optimized_thetas[best_iteration]
        best_loss = losses[best_iteration]

        print(f"Best Thetas from Iteration {best_iteration + 1}: {best_thetas}")
        print(f"Lowest Loss: {best_loss}")

        # Compute observed IVs
        y_obs = iv_new.ravel()  # Flattening the matrix for calculation ease

        # Compute predicted IVs using best_thetas
        y_pred = np.array([np.sqrt(svi_model(best_thetas, k, t) / t) for t in ttm for k in k_new])

        # Calculate SS_res
        SS_res = np.sum((y_obs - y_pred) ** 2)

        # Calculate SS_tot
        SS_tot = np.sum((y_obs - y_obs.mean()) ** 2)

        # Calculate R^2
        R2 = 1 - (SS_res / SS_tot)

        print(f"Coefficient of Determination (R^2): {R2:.4f}")

        # Check the R^2 value
        if R2 >= 0.97:
            break
        else:
            print("R^2 is below 0.8, rerunning the optimization...")

    # Now, let's check if the constraints are satisfied at theta_optimized
    print("Constraint 1:", constraint1(best_thetas))
    print("Constraint 2:", constraint2(best_thetas))
    print("Constraint 3:", constraint3(best_thetas))
    print("Constraint 4:", constraint4(best_thetas))

    # Now you can get the predicted IV for e.g. ttm=9 using the SVI model
    iv_svi_at_9 = np.sqrt(svi_model(best_thetas, k_new, ttm_of_interest) / ttm_of_interest)

    iv_svi_at_9_dict = {f"{k:.4f}": iv for k, iv in zip(k_new, iv_svi_at_9)}
    results_entry = {'Date': filename, 'R2': R2}
    results_entry.update(iv_svi_at_9_dict)
    results_list.append(results_entry)

    thetas_dict[filename] = best_thetas

# Path to read in the IV Matrix files for each day. Use the IR0 folder in the github.
path = "/home/RDC/miftachr/H:/miftachr/SVI/IR0"
os.chdir(path)

# Iterate over all CSV files in the directory.
# This is the main loop that processes each CSV file.
# I did it on the remote server. It might take some time to estimate all the IVs and parameters, run over night.
# Suggestion: just run the loop for a couple of days to see how it all works.
for filename in os.listdir(path):
    if filename.endswith('.csv') and filename.startswith('IV'):
        print(f"Processing {filename}...")
        # Process the current CSV file
        process_csv_file(filename)

# Convert the results list to a dataframe and save to a new CSV
results_df = pd.DataFrame(results_list)
# Convert the dictionary to a DataFrame
df_thetas = pd.DataFrame(thetas_dict).T
# Name columns as per the SVI model parameters
df_thetas.columns = ['a', 'b', 'rho', 'm', 'sigma', 'a_ttm', 'b_ttm', 'rho_ttm', 'm_ttm', 'sigma_ttm']

# Save the results to CSV. Use some local folder of yours.
df_thetas.to_csv('/home/RDC/miftachr/H:/miftachr/SVI/paras5b.csv', index=True)
results_df.to_csv('/home/RDC/miftachr/H:/miftachr/SVI/svi_iv_and_r2_results5b.csv', index=False)
