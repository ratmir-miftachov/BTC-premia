
import os
import math
import pandas as pd
import numpy as np
import re
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm

path="/Users/ratmir/Desktop/VIX/ttm27_new"
os.chdir(path)

def extract_info(filename):
    pattern = re.compile(r'(\d{8})_QW_T1_(\d+)_T2_(\d+).csv')
    match = pattern.match(filename)

    if match:
        date_str, t1_str, t2_str = match.groups()

        # Convert extracted strings to appropriate data types
        date = datetime.strptime(date_str, "%Y%m%d").date()
        t1 = int(t1_str)
        t2 = int(t2_str)

        return date, t1, t2
    else:
        print("Filename does not match the expected pattern.")
        return None


def calculate_vix_for_file(filename, date, ttm1, ttm2, tau):


    df = pd.read_csv(filename)

    data1 = df[['K_T1', 'C_T1', 'P_T1']].values.tolist()
    data2 = df[['K_T2', 'C_T2', 'P_T2']].values.tolist()

    data1_clean = [triple for triple in data1 if not all(np.isnan(val) for val in triple)]
    data2_clean = [triple for triple in data2 if not all(np.isnan(val) for val in triple)]

    large_number = 9999999  # or any other large number you prefer

    # Replace 0 with large_number for data1_clean
    data1_clean = [[val if val != 0 else large_number for val in triple] for triple in data1_clean]

    # Replace 0 with large_number for data2_clean
    data2_clean = [[val if val != 0 else large_number for val in triple] for triple in data2_clean]

    # Check-up1, s.t. at least one row in each ttm with put and call.
    data1_clean_np = np.array(data1_clean)
    differences1 = np.abs(data1_clean_np[:, 1] - data1_clean_np[:, 2])
    mask1 = differences1 < 10000

    data2_clean_np = np.array(data2_clean)
    differences2 = np.abs(data2_clean_np[:, 1] - data2_clean_np[:, 2])
    mask2 = differences2 < 10000

    # Check-up1
    if np.sum(mask1) >= 1 and np.sum(mask2) >= 1:
        #print("Both ttm1 and ttm2 contain at least one row with Call and Put price.")
        pass
    else:
        print("There is no option with put and call price for this strike price.")
        return None  # Return an empty DataFrame. If this applies, discard the .csv and continue with other .csv

    quotedata2 = [data1_clean, data2_clean]

    ##inputs
    rates = [0, 0]  # Assume IR=0 for now.
    T = [ttm1 / 365, ttm2 / 365]

    # HIER ANPASSEN!!! (einfach)
    # Compute F for near term and next term (p6)
    F = [None, None]
    for j in (0, 1):
        mindiff = None
        diff = None
        mindiff = None
        Fstrike = None
        Fcall = None
        Fput = None
        for d in quotedata2[j]:
            diff = abs(d[1] - d[2])  # HIER WIRD DER DURCHSCHNITT GENOMMEN ZWISCHEN BID UND ASK
            if (mindiff is None or diff < mindiff):  # das kann weg glaube ich
                mindiff = diff
                Fstrike = d[0]
                Fcall = d[1]
                Fput = d[2]
        F[j] = Fstrike + math.exp(rates[j] * T[j]) * (Fcall - Fput)  # diese zeile sollte so passen

    # select the options to be used in the VIX Index calculation (p6,7)
    #####HIER SOLLTE [STRIKE, option type, midpoint price=price in our case] einfach resultieren.
    #####k0 =[ , ] einfach Wert der direkt unter F liegt (welches im vorherigen schritt berechnet wurde). In diesem Fall 1960 für
    # near term and next term. der 'midpoint price' ist in diesem einen Fall dann der average vom put und vom call preis.
    selectedoptions2 = [[], []]
    k0 = [None, None]
    for j in (0, 1):
        i = 0
        for d in quotedata2[j]:
            if (d[0] < F[j]):
                k0[j] = d[0]
                k0i = i
            i += 1
        #this is my adjusted approch:
        if 9999999 in quotedata2[j][k0i]:
            k0i += 1

        d = quotedata2[j][k0i]
        ar = [d[0], 'put/call average', (d[1] + d[2]) / 2]
        selectedoptions2[j].append(ar)

        i = k0i - 1
        b = True
        previousbid = None
        while (b and i >= 0):
            d = quotedata2[j][i]
            if (d[2] > 0):
                ar = [d[0], 'put', d[2]]
                selectedoptions2[j].insert(0, ar)
            else:
                if (previousbid == 0): b = False
            previousbid = d[2]
            i -= 1

        i = k0i + 1
        b = True
        previousbid = None
        while (b and i < len(quotedata2[j])):
            d = quotedata2[j][i]
            if (d[1] > 0):
                ar = [d[0], 'call', d[1]]
                selectedoptions2[j].append(ar)
            else:
                if (previousbid == 0): b = False
            previousbid = d[1]
            i += 1

    # Check for 'zeros', which shouldn't be there, aka 999999 marked
    selectedoptions2[0] = [triplet for triplet in selectedoptions2[0] if 9999999 not in triplet]
    selectedoptions2[1] = [triplet for triplet in selectedoptions2[1] if 9999999 not in triplet]

    #the problem is that the selected row after the smallest difference, has a 0 entry, resulting in a large mid price (since 9999999)

    # Step 2: Calculate volatility for both near-term and next-term options (p8)
    # HIER WIRD DELTA_K berechnet, was einfach ein running average ist für jede transaktion. der vorherige und nachherige wert wird
    # genonmen und geaveraged.
    #### ICH DENKE MAN KANN ES SO LASSEN OHNE ANZUPASSEN
    for j in (0, 1):
        i = 0
        for d in selectedoptions2[j]:
            if (i == 0):
                deltak = selectedoptions2[j][1][0] - selectedoptions2[j][0][0]
            elif (i == len(selectedoptions2[j]) - 1):
                deltak = selectedoptions2[j][i][0] - selectedoptions2[j][i - 1][0]
            else:
                deltak = (selectedoptions2[j][i + 1][0] - selectedoptions2[j][i - 1][0]) / 2
            contributionbystrike2 = (deltak / (d[0] * d[0])) * math.exp(rates[j] * T[j]) * d[2]  #### d2 ist der 'midpoint price' = transaction price
            print(contributionbystrike2)
            selectedoptions2[j][i].append(contributionbystrike2)
            i += 1



    # DAS IST EINFACH NUR DIE SUMME DES ERSTEN TERMS!!! kann man so lassen.
    aggregatedcontributionbystrike = [None, None]
    for j in (0, 1):
        aggregatedcontributionbystrike[j] = 0
        for d in selectedoptions2[j]:
            aggregatedcontributionbystrike[j] += d[3]
        aggregatedcontributionbystrike[j] = (2 / T[j]) * aggregatedcontributionbystrike[j] # ca. [0.2 - 0.7]

    # sigma^2 wird berechnet. Keine anpassung erforderlich.
    sigmasquared = [None, None]
    for j in (0, 1):
        sigmasquared[j] = aggregatedcontributionbystrike[j] - (1 / T[j]) * (F[j] / k0[j] - 1) * (F[j] / k0[j] - 1)

    # Step 3: Calculate the 30-day weighted average of sigmasquared[0] and sigmasquared[1] (p9)
    # Gemäß Deribit:
    VIX = 100 * math.sqrt(((T[0] * sigmasquared[0]) * (T[1] - (tau / 365)) / (T[1] - T[0])


                           + (T[1] * sigmasquared[1]) * (
                (tau / 365) - T[0]) / (T[1] - T[0])) * 365 / tau)

    return pd.DataFrame({'Date': [date], 'VIX': [VIX]})


vix_df = pd.DataFrame(columns=['Date', 'VIX'])
all_data = []  # List to store all individual DataFrames

for filename in os.listdir(path):
    try:
        if filename.endswith('.csv'):
            print(f"Processing: {filename}")
            file_info = extract_info(filename)
            if file_info is not None:
                date, ttm1, ttm2 = file_info
                filepath = os.path.join(path, filename)
                new_vix_data = calculate_vix_for_file(filepath, date, ttm1, ttm2, tau=27)

                # Check if the DataFrame is not None
                if new_vix_data is not None:
                    all_data.append(new_vix_data)
                else:
                    print(f"No valid data in {filename}, skipping...")
    except Exception as e:
        print(f"An error occurred with file {filename}: {str(e)}")
        continue

# Concatenate all DataFrames in the list all_data into a single DataFrame
vix_df = pd.concat(all_data, ignore_index=True)

#Ensure the 'Date' column is a datetime type
vix_df['Date'] = pd.to_datetime(vix_df['Date'])

# Sort the DataFrame based on the 'Date' column
df_sorted = vix_df.sort_values(by='Date')

# If you want to reset the index after sorting
df_sorted.reset_index(drop=True, inplace=True)


#Fast solution for now:
df_sorted_filtered = df_sorted[df_sorted['VIX'] <= 170]

mask = df_sorted_filtered['Date'] >= '2017-07-01'        #deribit comparison: '2021-03-27'
df_sorted_filtered = df_sorted_filtered[mask]

#df_sorted_filtered.to_csv('btc_vix.csv', index=False)





# Calculating the 2-period EMA
ema = df_sorted_filtered['VIX'].ewm(span=3, adjust=False).mean()

#y = df_sorted_filtered['VIX']
#lowess_smoothing = sm.nonparametric.lowess(y, df_sorted_filtered.index, frac=0.008)
#ema = lowess_smoothing[:, 1]

# Adding the EMA to the original DataFrame
df_sorted_filtered.loc[df_sorted_filtered['VIX'].index, 'EMA'] = ema

#np.sum((common_data["BTC Volatility Index (DVOL)"] - common_data["EMA"])**2) # span2=25.5k

#save:
df_sorted_filtered.drop(df_sorted_filtered.columns[1], axis=1, inplace=True)

df_sorted_filtered.to_csv('btc_vix_EWA_27_new.csv', index=False)







# Plotting

file_path = '/Users/ratmir/Downloads/deribit-metrics_new.csv'

# Read the CSV file into a DataFrame
df_dvol = pd.read_csv(file_path, sep=';')

# Ensure the 'date' column is a datetime type
df_dvol['DateTime'] = pd.to_datetime(df_dvol['DateTime'])
mask = df_dvol['DateTime'] <= '2023-08-30'
df_dvol = df_dvol[mask]

df_dvol['BTC Volatility Index (DVOL)'] = pd.to_numeric(df_dvol['BTC Volatility Index (DVOL)'].str.replace(',', '.'))

########PLOT1 WITH EVENTS:


# Adjusting the figure size
plt.figure(figsize=(12, 8))

# Plotting df_dvol
plt.plot(df_dvol['DateTime'], df_dvol['BTC Volatility Index (DVOL)'], linestyle='-', marker='', color='green', label='dvol')

# Plotting df_sorted_filtered
plt.plot(df_sorted_filtered['Date'], df_sorted_filtered['EMA'], linestyle='-', marker='', color='b', label='VIX')

# Add events as vertical lines
dates_to_mark = pd.to_datetime(['2018-01-12', '2018-11-15', '2018-01-26', '2020-03-15', '2020-05-19', '2021-01-01', '2022-06-27', '2022-11-01'])
colors = ['red', 'green', 'black', 'purple', 'orange', 'brown', 'cyan', 'magenta']
event_names = ['Rumors South Korea could ban crypto trading', 'BTC capitalisation falls below $100b for first time since Oct 2017', 'Japans largest crypto market hacked', 'BTC falls by 30%', 'BTC drops by 30%. Major exchanges down.', 'BTC surpasses its previous ATH, then crashes.', 'Three Arrows Capital defaults', 'FTX crashes']

for date, color, event_name in zip(dates_to_mark, colors, event_names):
    plt.axvline(x=date, color=color, linestyle='-', linewidth=2, label=event_name)

# Labels, title, and formatting
plt.xlabel('Date')
plt.ylabel('Value')
plt.title('VIX and DVOL')
plt.grid(axis='y')
plt.ylim([40, 170])
plt.xticks(rotation=45)
plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=2)
plt.tight_layout(rect=[0, 0, 1, 0.95])

plt.show()


# Merging the two dataframes on their date columns to get common dates
common_data = pd.merge(df_dvol, df_sorted_filtered, left_on='DateTime', right_on='Date')

# Creating a plot figure
plt.figure(figsize=(12, 8))

# Plotting DVOL using merged common data
plt.plot(common_data['DateTime'], common_data['BTC Volatility Index (DVOL)'], linestyle='-', marker='', color='b', label='DVOL')

# Plotting VIX using merged common data
plt.plot(common_data['DateTime'], common_data['EMA'], linestyle='-', marker='', color='r', label='VIX')

# Adding labels, title, and grid
plt.xlabel('Date')
plt.ylabel('Value')
plt.title('DVOL vs VIX')
plt.grid(axis='y')

# Adding a legend in the best location
plt.legend(loc='best')

# Rotating date labels for better readability
plt.xticks(rotation=45)

# Display the plot
plt.tight_layout()
plt.show()



#common_data.drop('Date', axis=1, inplace=True)
#common_data.rename(columns ={ 'EMA' : 'VIX'}, inplace=True)
#common_data.to_csv('VIX_DVOL.csv', index=False)
