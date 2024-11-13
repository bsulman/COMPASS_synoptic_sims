
import pandas as pd
import glob
import xarray as xr


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


#----------------------------------------------------------------------------------
#  Run VECOS stations and save to file

df_goodwin = prep_vecos_waterquality_station(directory = '../../data/buoys/GoodwinIsland_CH019.38')
df_sweethall = prep_vecos_waterquality_station(directory = '../../data/buoys/SweetHallMarsh_PMK012.18')


#### CONVERT DEPTH TO HEIGHT !!!!
# TODO: Get the actual depth offset from sensor
df_goodwin = (df_goodwin
              .assign(water_height_m = lambda x: x.TOTAL_DEPTH-1.0)
              .assign(site='Goodwin Islands')
              .drop('TOTAL_DEPTH', axis=1))

df_sweethall = (df_sweethall
                .assign(water_height_m = lambda x: x.TOTAL_DEPTH-3.0)
                .assign(site='Sweet Hall Marsh')
                .drop('TOTAL_DEPTH', axis=1))


df_goodwin.columns = ['station','datetime','water_salinity', 'water_height_m', 'site']
df_sweethall.columns = ['station','datetime','water_salinity', 'water_height_m', 'site']


df_sweethall['water_height_m'] = df_sweethall['water_height_m'].apply(lambda x: x if -3 <= x <= 3 else np.nan)
# df_sweethall['water_height_m'] = df['water_height_m'].where(df['water_height_m'].between(min_value, max_value), np.nan)


#----------------------------------------------------------------------------------
# Read GCREW - Ben's file
fpath = '../../data/buoys/GCREW/Annapolis_CB3_3W_elev_sal_35yrs_NAVD.nc'

with xr.open_dataset(fpath, decode_times=False) as ds:
    print(ds)
    # Convert the 'temperature' variable to a pandas DataFrame
    gcrew = ds[['tide_height','tide_salinity']].to_dataframe().reset_index()
    gcrew['site'] = 'GCReW'
    gcrew['station'] = 'Annapolis'


# Define the start date and end date
start_date = '1984-01-01'
# Calculate the end date based on the number of rows and hourly intervals
end_date = pd.to_datetime(start_date) + pd.DateOffset(hours=len(gcrew) - 1)

# Create a date range with hourly intervals
date_range = pd.date_range(start=start_date, end=end_date, freq='H')

# Assuming 'df' is your existing DataFrame
# If 'df' is empty, you can create a new DataFrame using the date_range
# For example:
# gcrew = pd.DataFrame({'datetime': date_range})

# If 'df' is not empty and you want to add the datetime column
gcrew['datetime'] = date_range

#
# from datetime import timedelta, datetime
# # time_delta = timedelta(hours=gcrew['time'].tolist())
# # Subtract by the number of days between 0001-01-01 and 1970-01-01
# # TODO: Fix the time; verify with Ben
# gcrew['time'] = gcrew['time'] - 719164
# gcrew['datetime'] = pd.to_timedelta(gcrew['time'], unit='d')
#
# # Define the starting date
# start_date = pd.Timestamp('1970-01-01')
#
# # Add the timedelta to the start date
# gcrew['datetime'] = start_date + gcrew['datetime']
#
# # Round datetime to second
# gcrew['datetime'] = gcrew['datetime'].dt.round('1s')


gcrew = (gcrew
         .drop(['gridcell','time'], axis=1)
         .rename(columns={'tide_salinity':'water_salinity',
                          'tide_height':'water_height_m'})
         )

#----------------------------------------------------------------------------------
# GET NEW GCREW

# Define the directory and pattern
dirpat = '../../data/buoys/GCREW/CO-OPS_8575512*.csv'

# Find all files matching the pattern
files = glob.glob(dirpat, recursive=True)

# Initialize an empty list to store DataFrames
dfs = []

# Loop through the list of CSV files and read each one into a DataFrame
for file in files:
    df = pd.read_csv(file)
    dfs.append(df)

gcrew_water_height_df = \
    (pd.concat(dfs, ignore_index=True)

     .rename(columns={'Verified (m)': 'water_height_m'})

     .assign(water_height_m=lambda x: pd.to_numeric(x.water_height_m, errors='coerce'))
     .assign(datetime=lambda x: pd.to_datetime(x['Date'] + ' ' + x['Time (LST/LDT)']))
     .assign(station='NOAA-Annapolis-8575512')

     .drop(columns=['Preliminary (m)', 'Predicted (m)', 'Date', 'Time (LST/LDT)'])
     .drop_duplicates()
     .assign(site = 'GCReW')
     )




#----------------------------------------------------------------------------------
# Prep Moneystumps salinity
# TODO: Fix the large gaps

# Define the directory and pattern
dirpat = '../../data/buoys/Moneystump/salinity/*CEDR_tidal*.csv'

# Find all files matching the pattern
files = glob.glob(dirpat, recursive=True)
files

# Initialize an empty DataFrame
all_data = pd.DataFrame()

# Loop through the files and append to the DataFrame
for file in files:
    print(file)
    df = pd.read_csv(file)
    all_data = pd.concat([all_data, df])  #, ignore_index=True)

# Filter to station and salinity
moneystump_salinity = all_data[ ((all_data['MonitoringLocation']=='EE2.2') & (all_data['Parameter']=='SALINITY')) ]

# Convert to datetime and from GMT to eastern time
moneystump_salinity = \
    (moneystump_salinity
     .assign(datetime= lambda x: pd.to_datetime(x['SampleDate'] + ' ' + x['SampleTime']) -pd.Timedelta(hours=5))
     .assign(datetime= lambda x: x.datetime.round('60min'))
     .assign(site = 'Moneystump Swamp')
     .rename(columns={'MonitoringLocation':'station',
                      'MeasureValue':'water_salinity'})
     .drop_duplicates()
     )

# Subset columns
moneystump_salinity = moneystump_salinity[['site','station','datetime', 'water_salinity']]




# moneystump_salinity['datetime'].min()
# moneystump_salinity['datetime'].max()
# moneystump_waterheight['datetime'].min()
# moneystump_waterheight['datetime'].max()
# moneystump_salinity.columns


#----------------------------------------------------------------------------------
# Prep Moneystump water level
# There is a real data gap in 2013

# Define the directory and pattern
dirpat = '../../data/buoys/Moneystump/depth/*.csv'

files = glob.glob(dirpat, recursive=True)  # Find all files matching the pattern
all_data = pd.DataFrame()  # Initialize an empty DataFrame

# Loop through the files and append to the DataFrame
for file in files: # [0:1]:
    print(file)
    df = pd.read_csv(file)
    all_data = pd.concat([all_data, df])  #, ignore_index=True)

# Convert to datetime and from GMT to eastern time
all_data = \
    (all_data
     .assign(datetime= lambda x: pd.to_datetime(x['Date'] + ' ' + x['Time (GMT)']) -pd.Timedelta(hours=5))
     .assign(station='EE2.2' )
     .assign(site='Moneystump Swamp')
     .rename(columns= {'Verified (m)':'water_height_m'}))

# Filter columns
all_data = all_data[['site', 'station','datetime', 'water_height_m']]

moneystump_waterheight = all_data.copy().sort_values(by=['datetime']) # ascending=False)


#----------------------------------------------------------------------------------
#  COMBINE MONEYSTUMP SALINITY AND WATER LEVEL
# moneystump_df = (
#     moneystump_waterheight.merge(
#         moneystump_salinity,
#         on=['site','datetime'],
#         how='outer')
#     .assign(station = lambda x: np.where(pd.notnull(x.station_x), x.station_x, x.station_y))
#     )
#
# moneystump_df



#----------------------------------------------------------------------------------
#  Get NOAA buoy for Erie

import glob
folder_path = '../../data/buoys/Erie_Marblehead_noaa/'
files = glob.glob(os.path.join(folder_path, '*.csv'))

# Initialize an empty list to store DataFrames
dfs = []
# Loop through the list of CSV files and read each one into a DataFrame
for file in files:
    df = pd.read_csv(file)
    dfs.append(df)

# Concatenate all DataFrames in the list into a single DataFrame
marblehead_erie_df = (
    pd.concat(dfs, ignore_index=True)

    .rename(columns={'Verified (m)' : 'water_height_m'})

    .assign(water_height_m= lambda x: pd.to_numeric(x.water_height_m, errors='coerce'))
    .assign(datetime= lambda x: pd.to_datetime(x['Date'] + ' ' + x['Time (LST/LDT)']))
    .assign(station='Marblehead')
    .assign(water_salinity=0)

    .drop(columns=['Preliminary (m)','Predicted (m)', 'Date', 'Time (LST/LDT)'])
    .drop_duplicates()
    )


# Fill 'water_height_m' and 'water_salinity' with 0s if the station name is Marblehead
# df_filtered.loc[df_filtered['station'] == 'Marblehead', ['water_height_m', 'water_salinity']] = df_filtered.loc[df_filtered['station'] == 'Marblehead', ['water_height_m', 'water_salinity']].fillna(0)

erie_hydro_df_cc =  (marblehead_erie_df.copy().assign(site = 'Crane Creek'))
erie_hydro_df_owc = (marblehead_erie_df.copy().assign(site = 'Old Woman Creek'))
erie_hydro_df_pr =  (marblehead_erie_df.copy().assign(site = 'Portage River'))


# CONCATENATE REPEATED DFs
erie_hydro_df_3sites = pd.concat([erie_hydro_df_cc, erie_hydro_df_owc, erie_hydro_df_pr], axis=0)



#----------------------------------------------------------------------------------
#   USE GCREW SALINITY FOR MONEYSTUMP

gcrew_salinity_formoneystump = (
    gcrew.assign(site='Moneystump Swamp', station='GCReW input').drop(columns=['water_height_m', 'site', 'station']))

gcrew_formoneystump = (
    moneystump_waterheight
        # .drop(columns=['water_salinity'])
        .merge(
            gcrew_salinity_formoneystump,
            on=['datetime'],
            how='left')
        # .assign(station = lambda x: np.where(pd.notnull(x.station_x), x.station_x, x.station_y))
        )

#----------------------------------------------------------------------------------
# Combine data from each transect

df_wl = pd.concat([
        df_goodwin,
        df_sweethall,
        gcrew, # This is Ben's nc forcing
        gcrew_formoneystump,
        moneystump_waterheight,
        erie_hydro_df_3sites],
        axis=0)

# gcrew_water_height_df
# moneystump_salinity,


df_wl = df_wl.rename(columns={'site':'site_name'})

# Convert datatype
df_wl['water_salinity'] = pd.to_numeric(df_wl['water_salinity'], errors='coerce')
df_wl['water_height_m'] = pd.to_numeric(df_wl['water_height_m'], errors='coerce')
df_wl['datetime'] = pd.to_datetime(df_wl['datetime'], errors='coerce')

df_wl['zone_name'] = 'Water; Tidal forcing'

# Turn negative salintiy to 0
df_wl['water_salinity'] = df_wl['water_salinity'].apply(lambda x: max(x, 0))

# Save DataFrame to CSV
df_wl.to_csv('../../output/results/hydro_forcing_gauges/buoy_wl_all_syn_v4.csv', index=False)

# df_wl.info()
# df_wl.head()
# df_wl.columns


#----------------------------------------------------------------------------------
# df_goodwin.columns = ['station','datetime','water_salinity','water_depth_m']
# df_sweethall.columns = ['station','datetime','water_salinity','water_depth_m']
# gcrew = gcrew[['station','datetime','gridcell','water_height_m','water_salinity']]
# moneystump_salinity
# moneystump_waterheight

#
# df_wl.station.unique()
# # Top convert depth, we need:
# # Ht above LMSL (meters)	6.271
# boundary_wl_df = df_wl.copy()
#
# # Dictionary mapping old values to new labels
# mapping = {
#     'GoodwinIsland_CH019.38': 'Goodwin Islands',
#     'SweetHallMarsh_PMK012.18': 'Sweet Hall Marsh',
#     'GCREW': 'GCReW',
#     'Moneystump': 'Moneystump Swamp'
# }

# # Use map() to replace the values in the 'Location' column and create a new column 'Label'
# boundary_wl_df['site_name'] = boundary_wl_df['station'].map(mapping)
# # Set a new zone_name for buoys
# boundary_wl_df['zone_name'] = 'Tidal boundary; height (m)'



# gw_depth_df
# .assign(TIMESTAMP=lambda x: pd.to_datetime(x.TIMESTAMP),
#         TIMESTAMP_hourly=lambda x: x.TIMESTAMP.dt.floor('h'))
#
# .drop(columns=['TIMESTAMP', 'Instrument_ID', 'F_OOB', 'F_OOS'])  # 'Sensor_ID', 'Location', 'ID',
# .groupby(['Site', 'Plot', 'Instrument', 'TIMESTAMP_hourly'])  # , 'research_name'])  # 'Sensor_ID', 'Location',
# .mean()
# .reset_index()
# # .drop(columns=['Value'])
# )

# # Concatenate date and time columns
# all_data['datetime'] = all_data['Date'] + ' ' + all_data['Time (GMT)']
#
# # Convert to datetime
# all_data['datetime'] = pd.to_datetime(all_data['datetime'])
#
#
# all_data = all_data[['station','datetime', 'Verified (m)']]
#
# moneystump = all_data
#
# # Save the resulting DataFrame to a CSV file
# all_data.to_csv('../../../output/results/gauges/Moneystump_CO-OPS_8577330_hourly.csv', index=False)



# df_sweethall.to_csv('../../../output/results/gauges/SweetHallMarsh_PMK012.18_hourly.csv', index=False)
# df_goodwin.to_csv('../../../output/results/gauges/GoodwinIsland_CH019.38_hourly.csv', index=False)
