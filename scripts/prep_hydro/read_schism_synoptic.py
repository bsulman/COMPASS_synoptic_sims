


import geopandas as gpd
import pandas as pd
import numpy as np

# Read the spade-delimited CSV files
schism_pts = pd.read_csv('../../../data/schism/Salinity_in_ChesB_20170101-20181231/Salinity_Teri_v3.csv')

# Convert to points
schism_pts = (gpd.GeoDataFrame(schism_pts, geometry=gpd.points_from_xy(schism_pts.Longitude, schism_pts.Latitude, crs="EPSG:4326"))
             .to_crs("EPSG:26918")  # Reproject to DEM's NAD83 / UTM zone 18N
             # .rename(columns={"site": "site_id"})
             )

# Spatial join to transect point location
if 1: schism_pts.to_file('../../../output/schism_v3_salinity_pts.geojson')

#
schism_pts = schism_pts.dropna(subset=['site_name'])

#-------------------------------------------------------------------------------------#
# Read salinity

# Time series starting from Jan 1, 2017, time interval is 1 hr, time period is 728 days.
schism_dat = pd.read_csv('../../../data/schism/Salinity_in_ChesB_20170101-20181231/salt.surface.Salinity_Teri_v3.csv')

# Replace -99 NA values
schism_dat.replace(-99, np.nan, inplace=True)


#  Create a range of date:time values in hourly increments starting from 01-01-2017 00:00:00
# Append the date:time list as a new column to the combined dataframe
schism_dat.rename(columns={'date': 'datetime'}, inplace=True)
start_date = pd.to_datetime('2017-01-01 00:00:00')
schism_dat['datetime'] = pd.date_range(start=start_date, periods=len(schism_dat), freq='H')

#  Reshape df
schism_dat = schism_dat.melt(id_vars=['datetime'],
                       var_name='pt_id',
                       value_name='salinity')


schism_dat['pt_id'] = schism_dat['pt_id'].str.replace('pt_', '')
schism_dat['pt_id'] = schism_dat['pt_id'].astype(int)


#---------------------------------------------------------------------------------------
schism_dat = pd.merge(schism_dat, schism_pts, on='pt_id', how='right')
schism_dat.head(10)


schism_dat.to_csv('../../../output/syn_sites_schism_salininty.csv', index=False)

