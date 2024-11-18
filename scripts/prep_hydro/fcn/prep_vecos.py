
# Function preparing VECOS data for Goodwin and Sweethall
def prep_vecos_waterquality_station(directory):

    import pandas as pd
    import os

    # Initialize an empty list to store dataframes
    dfs = []

    # Loop through all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            filepath = os.path.join(directory, filename)
            dfs.append(pd.read_csv(filepath))              # Read the CSV file and append the dataframe to the list

    # Concatenate all dataframes in the list into a single dataframe
    df = pd.concat(dfs, ignore_index=True)
    # print(df.columns)

    # Ensure the 'time' column is in datetime format
    df['SAMPLE_DATETIME'] = pd.to_datetime(df['SAMPLE_DATETIME'])

    # Select columns
    df = df.loc[:, ['SAMPLE_DATETIME', 'SALINITY', 'TOTAL_DEPTH']]

    # Resample the DataFrame to hourly intervals and compute the mean
    df.set_index('SAMPLE_DATETIME', inplace=True)  # Set time as index
    df = df.resample('H').mean().reset_index()

    # write station
    df['STATION'] = os.path.basename(directory)

    # Convert to datetime
    df['SAMPLE_DATETIME'] = pd.to_datetime(df['SAMPLE_DATETIME'])

    df = df[['STATION', 'SAMPLE_DATETIME', 'SALINITY', 'TOTAL_DEPTH']]

    return(df)