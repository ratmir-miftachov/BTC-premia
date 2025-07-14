for name in list(globals()):
    if not name.startswith('_'):
        del globals()[name]


import os
import pandas as pd
import numpy as np

###############################################################################################################
################START OF MAIN CODE###############################################################################
###############################################################################################################


# This code gets the implied volatility surface using the estimated SVI coefficients.
# Some other stuff can be done when the cluster dates are used, but this is not of main interest in this code
# and I do not remember what it was used for.

# Path to read in the IV Matrix files for each day. Use the IR0 folder in the github.
path="/Users/ratmir/Downloads/testttm/update/IR0"
#path="/Users/ratmir/Downloads/testttm/IV_matrix_IR0"

os.chdir(path)
#This is the input from the SVI estimation, that we got from estimate_SVI_coefficients_each_day.py:
df1 = pd.read_csv('svi_iv_and_r2_results5.csv')
df2 = pd.read_csv('paras5.csv')

#C1 = pd.read_csv('dates_cluster1.csv')
#C0 = pd.read_csv('dates_cluster0.csv')


#these .pngs should be deleted
# del_dates = df1[df1['R2'] < 0.97].iloc[:, 0]
# folder_path = '/Users/ratmir/Desktop/Plots_IVs'  # Replace with the path to your folder containing the .png files
# for entry in del_dates:
#     # Extract the base name from the entry string (i.e., without .csv) and construct the .png filename
#     base_name = entry.replace('.csv', '')
#     png_filename = base_name + '_plot.png'
#
#     # Create the full path to the .png file
#     full_path = os.path.join(folder_path, png_filename)
#
#     # Check if the file exists and then delete it
#     if os.path.exists(full_path):
#         os.remove(full_path)
#         print(f"Deleted {png_filename}")
#     else:
#         print(f"{png_filename} not found")

df1 = df1[df1['R2'] >= 0.98] # 0.97; 761 remain # 0.98; 683 remain
paras = df2.loc[df1.index]
paras.columns.values[0] = 'Date'

print(paras.columns)
paras.columns = paras.columns.str.strip()

def svi_model(theta, k, tau):
    base_params = np.array(theta[:5])
    ttm_coeffs = np.array(theta[5:])
    a, b, rho, m, sigma = base_params + ttm_coeffs * tau
    return a + b * (rho * (k - m) + np.sqrt((k - m) ** 2 + sigma ** 2))


#You have to change the range of k_new, if you want to have a different range. Maybe this is what you want Zijin:
k_new = np.linspace(-0.15, 0.15, 100)
all_IVs = pd.DataFrame()
all_IVs_list = []
#ttms = list(range(3, 41))
# Set to other ttms, if you want to have the IVs for other ttms.
ttms = list([5, 5])  # or 9 9 , or 14 14 or 27 27

for ttm in ttms:
    all_IVs = pd.DataFrame()  # Initialize an empty DataFrame for the current ttm

    for file in paras['Date']:
        file_df = pd.read_csv(file)
        print(f"Interpolate IV for desired ttm in file {file}.")

        #extracting thetas
        theta = paras.loc[paras['Date'] == file]
        theta = theta.drop(theta.columns[0], axis=1)
        theta = np.squeeze(theta.values)

        IV = np.sqrt(svi_model(theta, k_new, ttm) / ttm)

        # Assuming IV is a list or array, convert IV into a dictionary with column names
        IV_dict = {str(k): [iv] for k, iv in zip(k_new, IV)}
        IV_dict['Date'] = file

        # Convert dictionary to DataFrame
        IV_df = pd.DataFrame(IV_dict)

        # Ensure 'Date' is the first column
        cols = ['Date'] + [col for col in IV_df if col != 'Date']
        IV_df = IV_df[cols]

        # Append to the main DataFrame
        all_IVs = pd.concat([all_IVs, IV_df], ignore_index=True)

    all_IVs['Date'] = all_IVs['Date'].str.extract(r'(\d{4}-\d{2}-\d{2})')
    all_IVs_list.append(all_IVs)


all_IVs.to_csv('interpolated_IV5_098.csv', index=False)


###############################################################################################################
################END OF MAIN CODE###############################################################################
###############################################################################################################

# For clusters:
all_IVs['Date'] = pd.to_datetime(all_IVs['Date'])
C0['Date'] = pd.to_datetime(C0['Date'])
C1['Date'] = pd.to_datetime(C1['Date'])


column_averages_list_C0 = []  # This will store the averages calculated from the filtered DataFrames
for df in all_IVs_list:
    # Convert the 'Date' column in the current DataFrame to datetime format
    df['Date'] = pd.to_datetime(df['Date'])
    # Filter the DataFrame to include only the rows with dates that are in C0
    filtered_df = df[df['Date'].isin(C0['Date'])]
    column_averages = filtered_df.select_dtypes(include=[np.number]).mean()
    averages_df = column_averages.to_frame().transpose()  # Convert the Series of averages to a DataFrame
    averages_df.reset_index(drop=True, inplace=True)  # Reset the index of the DataFrame for clean formatting
    column_averages_list_C0.append(averages_df)

column_averages_list_C1 = []  # This will store the averages calculated from the filtered DataFrames
for df in all_IVs_list:
    # Convert the 'Date' column in the current DataFrame to datetime format
    df['Date'] = pd.to_datetime(df['Date'])
    # Filter the DataFrame to include only the rows with dates that are in C0
    filtered_df1 = df[df['Date'].isin(C1['Date'])]
    column_averages1 = filtered_df1.select_dtypes(include=[np.number]).mean()
    averages_df1 = column_averages1.to_frame().transpose()  # Convert the Series of averages to a DataFrame
    averages_df1.reset_index(drop=True, inplace=True)  # Reset the index of the DataFrame for clean formatting
    column_averages_list_C1.append(averages_df1)


column_averages_list = []
for df in all_IVs_list:
    column_averages3 = df.select_dtypes(include=[np.number]).mean()
    averages_df3 = column_averages3.to_frame().transpose()
    averages_df3.reset_index(drop=True, inplace=True)
    column_averages_list.append(averages_df3)



# 3D plot setup
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection='3d')

# Plotting the average IVs for each ttm
for i, ttm in enumerate(ttms):
    # Extract the average IVs for the current ttm from the list
    avg_IVs = column_averages_list_C1[i].iloc[0].values  # Assuming each DataFrame in the list has a single row of averages

    # Plotting
    ax.plot(np.full_like(k_new, ttm), k_new, avg_IVs, label=f'Avg IV, TTM={ttm}', color='purple', linestyle='--')

# Set labels
ax.set_xlabel('Time to Maturity')
ax.set_ylabel('Log-Moneyness')
ax.set_zlabel('Implied Volatility')

plt.show()



# Combine the DataFrames, setting the index to the corresponding ttm values
combined_df = pd.concat(column_averages_list, keys=ttms)
combined_df.reset_index(level=0, inplace=True)
combined_df.rename(columns={'level_0': 'TTM'}, inplace=True)
combined_df.to_csv('overall_average_surface.csv', index=False)

combined_df0 = pd.concat(column_averages_list_C0, keys=ttms)
combined_df0.reset_index(level=0, inplace=True)
combined_df0.rename(columns={'level_0': 'TTM'}, inplace=True)
combined_df0.to_csv('average_surface0.csv', index=False)

combined_df1 = pd.concat(column_averages_list_C1, keys=ttms)
combined_df1.reset_index(level=0, inplace=True)
combined_df1.rename(columns={'level_0': 'TTM'}, inplace=True)
combined_df1.to_csv('average_surface1.csv', index=False)


#Double check: that is what I have used:
a=pd.read_csv('/Users/ratmir/Dropbox/CDI for Crypto/Updates/update_20231006to1017/interpolated IVs/interpolated_IV5_02_99.csv')


