<<<<<<< HEAD

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

df_goodwin = (prep_vecos_waterquality_station(directory = '../../data/buoys/GoodwinIsland_CH019.38'))
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


#----------------------------------------------------------------------------------
# Prep Moneystumps salinity

# Define the directory and pattern
dirpat = '../../data/buoys/Moneystump/salinity/*.csv'

# Find all files matching the pattern
files = glob.glob(dirpat, recursive=True)

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
     .assign(site = 'Moneystump Swamp')
     .rename(columns={'MonitoringLocation':'station',
                      'MeasureValue':'water_salinity'}))

moneystump_salinity.columns

# Subset columns
moneystump_salinity = moneystump_salinity[['site','station','datetime', 'water_salinity']]


#----------------------------------------------------------------------------------
# Prep Moneystump water level

# Define the directory and pattern
dirpat = '../../data/buoys/Moneystump/depth/*.csv'


files = glob.glob(dirpat, recursive=True)  # Find all files matching the pattern
all_data = pd.DataFrame()  # Initialize an empty DataFrame

# Loop through the files and append to the DataFrame
for file in files:# [0:1]:
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

moneystump_waterheight = all_data.copy()

moneystump_waterheight.info()


#----------------------------------------------------------------------------------
# Read Ben's file for GCREW
fpath = '../../data/buoys/GCREW/Annapolis_CB3_3W_elev_sal_35yrs_NAVD.nc'

with xr.open_dataset(fpath, decode_times=False) as ds:
    print(ds)
    # Convert the 'temperature' variable to a pandas DataFrame
    gcrew = ds[['tide_height','tide_salinity']].to_dataframe().reset_index()
    gcrew['site'] = 'GCReW'
    gcrew['station'] = 'Annapolis'


from datetime import timedelta, datetime
# time_delta = timedelta(hours=gcrew['time'].tolist())
# Subtract by the number of days between 0001-01-01 and 1970-01-01
# TODO: Fix the time; verify with Ben
gcrew['time'] = gcrew['time'] - 719164
gcrew['datetime'] = pd.to_timedelta(gcrew['time'], unit='d')

# Define the starting date
start_date = pd.Timestamp('1970-01-01')

# Add the timedelta to the start date
gcrew['datetime'] = start_date + gcrew['datetime']

# Round datetime to second
gcrew['datetime'] = gcrew['datetime'].dt.round('1s')


gcrew = (gcrew
         .drop(['gridcell','time'], axis=1)
         .rename(columns={'tide_salinity':'water_salinity',
                          'tide_height':'water_height_m'})
         )


#----------------------------------------------------------------------------------
#  Get NOAA buoy for Erie
folder_path = '../../data/buoys/Erie_Marblehead_noaa/'
csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

# Initialize an empty list to store DataFrames
dfs = []
# Loop through the list of CSV files and read each one into a DataFrame
for file in csv_files:
    df = pd.read_csv(file)
    dfs.append(df)

# Concatenate all DataFrames in the list into a single DataFrame
marblehead_erie_df = (
    pd.concat(dfs, ignore_index=True)

    .rename(columns={'Verified (m)' : 'water_height_m'})
    .assign(water_height_m= lambda x: pd.to_numeric(x.water_height_m, errors='coerce'))

    .assign(datetime= lambda x: pd.to_datetime(x['Date'] + ' ' + x['Time (LST/LDT)']))
    .assign(station='Marblehead')
    .drop(columns=['Preliminary (m)','Predicted (m)', 'Date', 'Time (LST/LDT)'])
    )

erie_hydro_df_cc =  (marblehead_erie_df.copy().assign(site = 'Crane Creek'))
erie_hydro_df_owc = (marblehead_erie_df.copy().assign(site = 'Old Woman Creek'))
erie_hydro_df_pr =  (marblehead_erie_df.copy().assign(site = 'Portage River'))


# CONCATE REPEATED DFs
erie_hydro_df_3sites = pd.concat([erie_hydro_df_cc, erie_hydro_df_owc, erie_hydro_df_pr], axis=0)



#----------------------------------------------------------------------------------
# Combine data from each transect


# Combine
df_wl = pd.concat([
        df_goodwin,
        df_sweethall,
        gcrew,
        moneystump_salinity,
        moneystump_waterheight,
        erie_hydro_df_3sites],
        axis=0)

df_wl = df_wl.rename(columns={'site':'site_name'})

# Convert datatype
df_wl['water_salinity'] = pd.to_numeric(df_wl['water_salinity'], errors='coerce')
df_wl['water_height_m'] = pd.to_numeric(df_wl['water_height_m'], errors='coerce')
df_wl['datetime'] = pd.to_datetime(df_wl['datetime'], errors='coerce')

df_wl['zone_name'] = 'Water; Tidal forcing'



df_wl.info()
df_wl.head()
# df_wl.columns

# Save DataFrame to CSV
df_wl.to_csv('../../output/results/hydro_forcing_gauges/buoy_wl_all_syn_v2.csv', index=False)


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
||||||| af2305f
=======

# Function preparing Goodwin and
def prep_waterquality_station(directory):

    import pandas as pd
    import os

    # Initialize an empty list to store dataframes
    dfs = []

    # Loop through all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            filepath = os.path.join(directory, filename)
            # Read the CSV file and append the dataframe to the list
            dfs.append(pd.read_csv(filepath))

    # Concatenate all dataframes in the list into a single dataframe
    df = pd.concat(dfs, ignore_index=True)

    # Ensure the 'time' column is in datetime format
    df['SAMPLE_DATETIME'] = pd.to_datetime(df['SAMPLE_DATETIME'])

    # df = df['STATION','SAMPLE_DATETIME', 'SALINITY', 'TOTAL_DEPTH']
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
# Save to file

df_goodwin = prep_waterquality_station(directory = '../../../data/buoys/GoodwinIsland_CH019.38')
df_goodwin.to_csv('../../../output/results/gauges/GoodwinIsland_CH019.38_hourly.csv', index=False)

df_sweethall = prep_waterquality_station(directory = '../../../data/buoys/SweetHallMarsh_PMK012.18')
df_sweethall.to_csv('../../../output/results/gauges/SweetHallMarsh_PMK012.18_hourly.csv', index=False)



#----------------------------------------------------------------------------------
# Prep Moneystumps

import pandas as pd
import glob

# Define the directory and pattern
dirpat = '../../../data/buoys/Moneystump/*.csv'

# Find all files matching the pattern
files = glob.glob(dirpat)

# Initialize an empty DataFrame
all_data = pd.DataFrame()

# Loop through the files and append to the DataFrame
for file in files:
    df = pd.read_csv(file)
    all_data = pd.concat([all_data, df], ignore_index=True)



# Concatenate date and time columns
all_data['datetime'] = all_data['Date'] + ' ' + all_data['Time (GMT)']

# Convert to datetime
all_data['datetime'] = pd.to_datetime(all_data['datetime'])

all_data['station'] = 'Moneystump'

all_data = all_data[['station','datetime', 'Verified (m)']]

moneystump = all_data

# Save the resulting DataFrame to a CSV file
all_data.to_csv('../../../output/results/gauges/Moneystump_CO-OPS_8577330_hourly.csv', index=False)


#----------------------------------------------------------------------------------
# Read file for GCREW

import xarray as xr
import pandas as pd

fpath = '../../../data/buoys/GCREW/Annapolis_CB3_3W_elev_sal_35yrs_NAVD.nc'

with xr.open_dataset(fpath, decode_times=False) as ds:
    print(ds)
    # Convert the 'temperature' variable to a pandas DataFrame
    gcrew = ds[['tide_height','tide_salinity']].to_dataframe().reset_index()
    gcrew['station'] = 'GCREW'
print(gcrew)

from datetime import timedelta, datetime
# time_delta = timedelta(hours=gcrew['time'].tolist())

# gcrew['days'] = pd.to_timedelta(gcrew['time'], unit='D')

# Subtract by the number of days between 0001-01-01 and 1970-01-01
gcrew['time'] = gcrew['time'] - 719164
gcrew['datetime'] = pd.to_timedelta(gcrew['time'], unit='d')

# Define the starting date
start_date = pd.Timestamp('1970-01-01')

# Add the timedelta to the start date
gcrew['datetime'] = start_date + gcrew['datetime']

# Round datetime to second
gcrew['datetime'] = gcrew['datetime'].dt.round('1s')

#----------------------------------------------------------------------------------
# Combine data from each transect

df_goodwin.columns = ['station','datetime','tide_salinity','total_depth']
df_sweethall.columns = ['station','datetime','tide_salinity','total_depth']

gcrew = gcrew[['station','datetime','gridcell','tide_height','tide_salinity']]

moneystump.columns = ['station','datetime','tide_height']

# df_wl.columns

# Combine
df_wl = pd.concat([df_goodwin, df_sweethall, gcrew, moneystump], axis=0)
# Write DataFrame to CSV
df_wl.to_csv('../../../output/results/gauges/buoy_wl_all_syn.csv', index=False)

#----------------------------------------------------------------------------------
#  Process data for plot

import pandas as pd

# Reread
df_wl = pd.read_csv('../../../output/results/gauges/buoy_wl_all_syn.csv', low_memory=False)

# Convert datatype
df_wl['tide_height'] = pd.to_numeric(df_wl['tide_height'], errors='coerce')
df_wl['total_depth'] = pd.to_numeric(df_wl['total_depth'], errors='coerce')
df_wl['datetime'] = pd.to_datetime(df_wl['datetime'], errors='coerce')

# df_wl = df_wl.head(10000)
start_date = '2018-01-01'
end_date = '2023-12-31'

# Filter DataFrame by date range
df_wl = df_wl[(df_wl['datetime'] >= start_date) & (df_wl['datetime'] <= end_date)]

df_wl.station.unique()


##!!!!!!
from plotnine import ggplot, aes, theme, geom_point, theme_minimal,  labs, geom_histogram, coord_flip, facet_wrap
#----------------------------------------------------------------------------------
# Make depth time series plot

# depth_plot = \
(
    ggplot(df_wl) +
    geom_point(aes(x='datetime', y='total_depth', color='station'), size=0.1) +
    labs(x='', y='Water depth (m)')
).save('../../../output/figures/timeseries_depth.png',
       width=8, height=3, dpi=300, verbose = False)


#----------------------------------------------------------------------------------
# Make water height time series plot
(
    ggplot(df_wl, aes(x='datetime', y='tide_height', color='station')) +
    geom_point(size=0.1) +
    labs(x='', y='Water Level (NAVD, m)')
).save('../../../output/figures/timeseries_tide_height.png',
       width=8, height=3, dpi=300, verbose = False)


#----------------------------------------------------------------------------------
#  PLOT  DISTRIB HEIGHT
plot = (ggplot(df_wl, aes(x='tide_height', fill='station'))
        + geom_histogram(binwidth=0.1, color=None)
        + coord_flip()
        + facet_wrap('~station', ncol=2, nrow=2)
        # + ggtitle("Histogram of Randomly Generated Data")
        + labs(x="Water height (NAVD, m)", y="Frequency of hourly measurements")
        + theme(legend_position='none')
        # + theme_minimal()
        ).save('../../../output/figures/distrib_tide_height.png',
               width=4, height=6, dpi=300, verbose = False)

#----------------------------------------------------------------------------------
#  PLOT  DISTRIB DEPTH
plot = (ggplot(df_wl, aes(x='total_depth', fill='station'))
        + geom_histogram(binwidth=0.1, color=None)
        + coord_flip()
        + facet_wrap('~station', ncol=2, nrow=2)
        # + ggtitle("Histogram of Randomly Generated Data")
        + labs(x="Water depth (m)",  y="Frequency of hourly measurements")
        + theme(legend_position='none')
        # + theme_minimal()
        ).save('../../../output/figures/distrib_total_depth.png',
               width=4, height=6, dpi=300, verbose = False)


#----------------------------------------------------------------------------------
# Make salinity plot
(
    ggplot(df_wl, aes(x='datetime', y='tide_height', color='station')) +
    geom_point(size=0.6) +
    # theme_bw()
    labs(x='', y='Water Level (m; NAVD)')  # title='Water depth (m)',
).save('../../../output/figures/tide_height_plot.png', width=8, height=6, dpi=300, verbose = False)




# Save plot to file
# depth_plot.save('../../../output/figures/depth_plot.png', width=8, height=6, dpi=300, verbose = False)


#----------------------------------------------------------------------------------
# Create the point graph using plotnine #
salinity_plot = (
    ggplot(df, aes(x='SAMPLE_DATETIME', y='SALINITY')) +
    geom_point(color='#FF5733') +
    theme_minimal()
    # labs(title='Water Level vs Time', x='Time', y='Water Level')
)

salinity_plot.save('../../../output/figures/goodwin_salinity_plot.pdf', width=6, height=4)
e('../../../output/figures/goodwin_waterdepth_plot.pdf', width=6, height=4)





# depth_plot.show()

# geom_point(color='#8B0000') +
# Print the plot object to display the plot
# print(depth_plot)
# depth_plot.sav

# Read the CSV file into a DataFrames
# Replace '/path/to/your/file.csv' with the actual file path
# df = pd.read_csv('/path/to/your/file.csv')

# Subtract the number of hours by 621355, which is the number of hours between 0001-01-01 and 1970-01-01
# pandas-dateime, has problems dealing with long ranges, bc it is computed in nanoseconds
# gcrew['datetime'] = pd.to_timedelta(gcrew['time'], unit='h')  # - 621355
>>>>>>> newforcings_rebased
