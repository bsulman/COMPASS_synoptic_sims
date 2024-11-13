import pandas as pd
import numpy as np
import os



df_wl = ( \
    pd.read_csv('../../output/results/hydro_forcing_gauges/buoy_wl_all_syn_v4.csv')
    .assign(datetime = lambda x: pd.to_datetime(x.datetime))
    )

# Filter the 'datetime' column between 2006-01-01 and 2021-12-31
mask = (df_wl['datetime'] >= '2006-01-01') & (df_wl['datetime'] <= '2020-12-31')
df_wl = df_wl.loc[mask]


# /--------------------------------------------------------------------
#/  Filter outliers

# Define the rolling window size and z-score threshold
window_size = 365*5
z_score_threshold = 1.5

# Calculate rolling mean, std, z-score, and filter based on z-score threshold
df_wl = (
    df_wl.groupby(['site_name', 'station', 'zone_name'], group_keys=False)
    .apply(lambda x: x.assign(
        water_salinity_rolling_mean=x['water_salinity'].rolling(window=window_size, min_periods=10, center=True).mean(),
        water_salinity_rolling_std=x['water_salinity'].rolling(window=window_size, min_periods=10, center=True).std(),
        salinity_z_score=lambda df: (df['water_salinity'] - df['water_salinity_rolling_mean']) / df['water_salinity_rolling_std'],

        elev_rolling_mean=x['water_height_m'].rolling(window=window_size, min_periods=10, center=True).mean(),
        elev_rolling_std=x['water_height_m'].rolling(window=window_size, min_periods=10, center=True).std(),
        elev_z_score=lambda df: (df['water_height_m'] - df['elev_rolling_mean']) / df['elev_rolling_std']))

    # .apply(lambda x: x.assign(
    .assign(
        water_salinity= lambda x: np.where(abs(x.salinity_z_score) > z_score_threshold, np.nan, x.water_salinity),
        water_height_m= lambda x: np.where(abs(x.elev_z_score) > z_score_threshold, np.nan, x.water_height_m)
            )
        )

# gw_depth_df.info()

#-----------------------------------------------------------
# Set the 'datetime' column as index
df_wl.set_index('datetime', inplace=True)

# Create an empty DataFrame to store results
filled_df = pd.DataFrame()


# Ensure each hourly timestep exists per 'site_name'
for site_name, group in df_wl.groupby(['site_name','station']):

    # Remove duplicates in the index
    group = group[~group.index.duplicated(keep='first')]

    # Resample to hourly frequency to fill gaps
    group = group.resample('h').asfreq()

    # Forward fill NaN values for 'water_height_m' and 'water_salinity'
    group[['water_height_m', 'water_salinity']] = group[['water_height_m', 'water_salinity']].ffill()

    # Add the 'site_name' back as a column
    group['site_name'] = site_name[0]

    # Append to the final DataFrame
    filled_df = pd.concat([filled_df, group])

# Reset the index of the resulting DataFrame
filled_df.reset_index(inplace=True)

print(filled_df)


#----------------------------------------------------------------------------------
# Save DataFrame to CSV
filled_df.to_csv('../../output/results/hydro_forcing_gauges/buoy_wl_all_syn_v4_filled.csv',
                 index=False)


# df_wl = df_wl[df_wl['site_name'] == 'Moneystump Swamp']  #'Sweet Hall Marsh']
# df_sorted = df_wl.sort_values(by=['site_name', 'datetime'], ascending=False)
# df_sorted