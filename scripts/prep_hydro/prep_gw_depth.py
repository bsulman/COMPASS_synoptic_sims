# Prep synoptic sensor data v1.1
# To download from COMPASS HPC:
# rsync -avz <user>@compass.pnl.gov:/compass/datasets/fme_data_release/sensor_data/Level1/v1-1 .

import os
import glob
import zipfile
import pandas as pd
import numpy as np


# /--------------------------------------------------------------------
#/
def extract_and_filter_zip_files(directory):

    # Find all .zip files in the directory recursively
    zip_files = glob.glob(os.path.join(directory, '**', '*.zip'), recursive=True)

    # Initialize an empty DataFrame to store results
    result_df = pd.DataFrame()

    for zip_file in zip_files: #[0:1]:

        with zipfile.ZipFile(zip_file, 'r') as z:
            # List all files in the zip archive
            file_names = z.namelist()

            # Process each CSV file in the archive
            for file_name in file_names:

                if file_name.endswith('.csv'):
                    print(file_name)

                    # Read the CSV file into a DataFrame
                    with z.open(file_name) as f:

                        # try:
                        # Read in file, filter out rows that have flags
                        df = (pd.read_csv(f)
                              .query('F_OOB!=1')
                              .query('F_OOS!=1'))

                        # Check if the 'type' column exists
                        if 'research_name' in df.columns:

                            # Filter rows where 'type' column matches 'gw_pressure'
                            subset_df = df[df['research_name'].isin(["gw_pressure", "gw_density", "gw_temperature", "gw_salinity"])] #'gw_pressure']

                            # Append to the result DataFrame
                            result_df = pd.concat([result_df, subset_df], ignore_index=True)

                        # except Exception as e:
                            # print(f"Error processing file {file_name} in {zip_file}: {e}")
                            # continue
    return result_df


# /--------------------------------------------------------------------
#/  Apply the functions to the directory

# Set directory where sensor data is stored
directory = '../../data/synoptic_sensors'

# Combine all gw_pressure sensor data together
gw_depth_df = extract_and_filter_zip_files(directory)

# Pivot table to gw_ to columns
gw_depth_df = (
    gw_depth_df
    .drop(columns=['ID'])
    .reset_index()
    # Remove these two NaN filled columns
    # 'Location','Sensor_ID',
    .pivot_table(index=['Site', 'Plot','TIMESTAMP', 'Instrument', 'Instrument_ID','F_OOB', 'F_OOS'],
                 columns='research_name', values='Value').reset_index() # , fill_value=NULL
    )



# /--------------------------------------------------------------------
#/   Average values from 15min intervals to hourly
gw_depth_df = (
    gw_depth_df
    .assign(TIMESTAMP = lambda x: pd.to_datetime(x.TIMESTAMP),
            TIMESTAMP_hourly = lambda x: x.TIMESTAMP.dt.floor('h'))

    .drop(columns=['TIMESTAMP', 'Instrument_ID', 'F_OOB', 'F_OOS'])  # 'Sensor_ID', 'Location', 'ID',
    .groupby(['Site', 'Plot', 'Instrument',  'TIMESTAMP_hourly'])#, 'research_name'])  # 'Sensor_ID', 'Location',
    .mean()
    .reset_index()
    # .drop(columns=['Value'])
    )


# /--------------------------------------------------------------------
# / Join well depth measure with DEM elev
#/   To Convert to height from NADV88

# Read in table with full names
# TODO: Fix the elevation order in Gcrew and other sites

#[['site_id','zone','elev']]

synoptic_elev = pd.read_csv('../../output/results/elev/' + 'synoptic_elev_zone_v3.csv')

# For some reason, only string list in the function itself, not alias, works.
synoptic_elev = (
    synoptic_elev.assign(
        elev_ft    =np.where(synoptic_elev['site_name'].isin(['Portage River', 'Old Woman Creek','Crane Creek']), synoptic_elev['elev'], synoptic_elev['elev']*0.3048),
        elev_m     =np.where(synoptic_elev['site_name'].isin(['Portage River', 'Old Woman Creek','Crane Creek']), synoptic_elev['elev']*0.3048, synoptic_elev['elev'])
        )
    .drop(columns=['elev'])
    )
synoptic_elev



# /--------------------------------------------------------------------
#/  Join ground elev to WTD
# This is where zones are filtered to: W, TR, UP;   changed to left to keep 'WTE' and 'SWAMP'

gw_depth_df= (pd.merge(gw_depth_df,
                       synoptic_elev,
                       left_on=['Site', 'Plot'],
                       right_on=['site_id', 'zone_id'],
                       how='left')
               )

gw_depth_df.info()
gw_depth_df.head()


# /--------------------------------------------------------------------
#/ Correct depth with well sensor height

#Calculate water depth from pressure, density, and well data
#gw_density;  L1 data bounds: 0.98, 1.05; units g/cm3
#gw_pressure; sensor units: psi; L1 data set units: mbar
#L1 data bounds: -10, 910; Info: AQ600 Vented pressure already corrected for barometric pressure

well_dimensions = pd.read_csv('../../data/synoptic_sensors/Aquatroll_installation_info_092024.csv').iloc[:, 0:14]
well_dimensions = (
    well_dimensions
    .assign(ground_to_sensor_cm = lambda x: x.ring_to_pressure_sensor_cm - (x.well_top_to_ground_cm - x.bolt_to_cap_cm))
    .drop('ground_to_sensor_cm = ring_to_pressure_sensor_cm - (well_top_to_ground_cm - bolt_to_cap_cm', axis=1)
    )

# Join well dimension
gw_depth_df = (
    pd.merge(gw_depth_df,
             well_dimensions,
                       left_on=['site_id', 'zone_name'],
                       right_on=['site', 'transect_location'],
                       how='inner'))


gw_depth_df = (
    gw_depth_df
    .assign(
        # Convert to water depth (h = P [mbar] * 100 [Pa/mbar])/(rho [g/cm3]*1000 [kg/m3//g/cm3]*g [m/s2]) where [Pa]=[kgm/s2m2];  9.80665 = specific gravity
        pressurehead_m = lambda x: (x.gw_pressure * 100) / (x.gw_density * 1000 * 9.80665),
        # water level below surface of ground (divide ground to sensor so it is in m) subtract ground to sensor from pressure head
        wl_below_surface_m = lambda x: x.pressurehead_m - (x.ground_to_sensor_cm / 100))

    #  CALCULATE WATER LEVEL ELEVATION
    .assign(gw_elev_m = lambda x: x.elev_m + x.wl_below_surface_m)
    )



# /--------------------------------------------------------------------
#/  Filter outliers

# Define the rolling window size and z-score threshold
window_size = 365*5
z_score_threshold = 1.5

# Calculate rolling mean, std, z-score, and filter based on z-score threshold
gw_depth_df = (
    gw_depth_df.groupby(['Site', 'Plot', 'Instrument'], group_keys=False)
    .apply(lambda x: x.assign(
        salinity_rolling_mean=x['gw_salinity'].rolling(window=window_size, min_periods=1).mean(),
        salinity_rolling_std=x['gw_salinity'].rolling(window=window_size, min_periods=1).std(),
        salinity_z_score=lambda df: (df['gw_salinity'] - df['salinity_rolling_mean']) / df['salinity_rolling_std'],

        elev_rolling_mean=x['gw_elev_m'].rolling(window=window_size, min_periods=1).mean(),
        elev_rolling_std=x['gw_elev_m'].rolling(window=window_size, min_periods=1).std(),
        elev_z_score=lambda df: (df['gw_elev_m'] - df['elev_rolling_mean']) / df['elev_rolling_std']))

    # .apply(lambda x: x.assign(
    .assign(
        gw_salinity= lambda x: np.where(abs(x.salinity_z_score) > z_score_threshold, np.nan, x.gw_salinity),
        gw_elev_m= lambda x: np.where(abs(x.elev_z_score) > z_score_threshold, np.nan, x.gw_elev_m)
            )
        )

# gw_depth_df.info()


# /--------------------------------------------------------------------
#/  Write synoptic well data to a CSV file
output_filename = '../../output/results/sensor_gauges/synoptic_gw_elev_v2.csv'
gw_depth_df.to_csv(output_filename, index=False)












# .query('abs(elev_z_score) <= @z_score_threshold')
# assign(AdjustedValue=np.where(df['Value'] > 25, df['Value'] * 2, df['Value'] / 2))

# def calc_gw_depth(p):
#     # Convert from millibar to psi
#     p_psi = p * 0.0145038
#     # Convert to depth (m)
#     d = (0.703073 * p_psi) / 9.807
#     return d


# Convert to depth
# This how EFluet did conversion initially
# gw_depth_df['gw_depth_m'] = calc_gw_depth(gw_depth_df.Value)


#---------------------------------------------------------------------
#!!!!!!!!!!!!!!!!!!!!!!!!
# Translated R code from Steph W.
# results = []  # Initialize list to store data
# # Loop through each file
# for f in files:
#     print(f)
#     selected_research_names = ["gw_pressure", "gw_density", "gw_temperature", "gw_salinity"]
#
#     # Read CSV data
#     dat = pd.read_csv(f)
#
#     # Filter for "AquaTROLL600" and selected research names
#     troll = dat[dat['Instrument'] == "AquaTROLL600"]
#     gw = troll[troll['research_name'].isin(selected_research_names)]
#
#     # Select required columns
#     gw = gw[['TIMESTAMP', 'research_name', 'Value', 'F_OOB', 'F_OOS', 'Plot', 'Site']]
#     results.append(gw)
#
# # Combine all data into a single DataFrame
# dat = pd.concat(results).reset_index(drop=True)
#
# # Convert to wide format
# gw1 = dat.pivot_table(index=['TIMESTAMP', 'Plot', 'Site'], columns='research_name', values='Value').reset_index()
# print(gw1.head())
# #!!!!!!!!!!!!!!!!!!!!!!!!



# /--------------------------------------------------------------------
# /--------------------------------------------------------------------
# /--------------------------------------------------------------------
#/   Join to append full names; THIS ALSO EXCLUDE SWAMP AND WLT ZONES
# gw_depth_df = pd.read_csv('../../output/results/sensor_gauges/synoptic_gw_pressure.csv')
# gw_depth_df.head()
# #  MACHINE LEARNING  OUTLIER DETECTION
# # https://eyer.ai/blog/anomaly-detection-in-time-series-data-python-a-starter-guide/
# from sklearn.neighbors import LocalOutlierFactor
# import pandas as pd
#
# model = LocalOutlierFactor()
# X = gw_depth_df[['gw_depth_m']].dropna()
# model.fit(X)
# y_pred = model.fit_predict(X)
# X[y_pred == -1] # anomalies


# Elevation profile
# + geom_line(outdf_j, aes(x='dist', y="elev_fromwetland", color="site_id"), size=0.9)
#
# # Zone labels # y="elev_fromwetland+.5",
# + geom_text(outdf_j.dropna(subset=['zone']),
#             aes(x='dist', y=-0.25, label="zone", color="site_id"),
#             size=7, angle=90, va='top')
# # Label each transect
# + geom_text(outdf_j.dropna(subset=['zone']).query('zone=="Upland"'),
#             aes(x='dist+1', y="elev_fromwetland+.1", label="site_id", color="site_id"),
#             size=9, fontweight='5', angle=90, ha='left', va='bottom')

# + scale_y_continuous(limit)
# + facet_wrap("~site_id", scales="free", ncol=4)



# Downloaded data from
# gw_pressure          psi          mbar       -10, 910     Vented pressure corrected for barometric pressure


# Convert pressure to depth
# https://in-situ.com/en/faq/maintenance-calibration-and-service-tips/maintenance-calibration-and-service-faqs/how-are-depth-and-pressure-related
# D = Depth in meters
# P = Pressure in PSI
# SG = Specific Gravity


# Local gravity estimator
# https://www.sensorsone.com/local-gravity-calculator/
# https://geodesy.noaa.gov/cgi-bin/grav_pdx.prl
# D = (0.703073 X P) / SG

