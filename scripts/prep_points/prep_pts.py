
import os
import numpy as np
import numpy.ma as ma
import pandas as pd
import geopandas as gpd
# import fiona
# import rasterstats as rs
# from rasterstats import zonal_stats
# import rasterio as rio
# from matplotlib import pyplot


# --------------------------------------------------------------------------------------------------------------------
# Read file of synoptic site coords
synoptic = pd.read_csv('../data/raw/transect_coords/compass_synoptic.csv')
    # .query('region=="Chesapeake Bay"'))  # Filter to Chesapeake Bay

# TODO: are the original coordinates from Ben on WGS84 or NAD83 datum?
synoptic = \
    (gpd.GeoDataFrame(synoptic, geometry=gpd.points_from_xy(synoptic.long, synoptic.lat, crs="EPSG:4269"))
    .to_crs("EPSG:26918")  # Reproject to DEM's CRS: NAD83 / UTM zone 18N
    .rename(columns={"site": "site_id"})
    )

# synoptic['site_cat'] = 'synoptic'
# synoptic.info()

synoptic_wgs84 = (synoptic.to_crs("EPSG:4326").reset_index())

# Save synoptic points to file
synoptic_wgs84.to_file('../data/processed/synoptic_pts_wgs84.geojson')



#--------------------------------------------------------------------------
#%% Get EXCHANGE sites

# Declare columns to keep
cols2keep = \
    ['kit_id', 'water_latitude', 'water_longitude', 'sediment_latitude', 'sediment_longitude',
    'wetland_latitude', 'wetland_longitude', 'transition_latitude', 'transition_longitude',
    'upland_latitude', 'upland_longitude']

# Read file of site locations;
# FIXME: Modified input longitude for two points;  one missing minus sign; other was lat=29 not 39
ex_sites = \
    (pd.read_csv('../../../data/exchange/EC1_Metadata_CollectionLevel_EFmod.csv')
    .loc[:, cols2keep]
    .melt(id_vars='kit_id'))

# Split column names into two; split by underscore
ex_sites[['zone', 'var']] = pd.DataFrame(ex_sites.variable.str.split('_').tolist(), columns=['zone', 'variable2'])

# Drop "var" column
ex_sites = ex_sites.drop(columns=['variable'])

# pivot lat/long into different columns
ex_sites = pd.pivot_table(ex_sites, index=['kit_id', 'zone'], values='value', columns='var')

# Convert coords to point
ex_sites = (
    gpd.GeoDataFrame(ex_sites, geometry=gpd.points_from_xy(ex_sites.longitude, ex_sites.latitude, crs="EPSG:4269"))
    .to_crs("EPSG:26918")
    .reset_index()
    .rename(columns={"kit_id": "site_id"}))

ex_sites['site_cat'] = 'exchange'

#--------------------------------------------------------------------------
#%% Combine sites
all_sites_utm = (pd.concat([ex_sites, syn_sites])
            .reset_index())


all_sites_wgs84 = (all_sites_utm.to_crs("EPSG:4326"))
            #        (pd.concat([ex_sites.to_crs("EPSG:4326"),
            #            syn_sites.to_crs("EPSG:4326")])
            # .reset_index()))


#--------------------------------------------------------------------------
# Save points
if 1:
    all_sites_utm.to_file('../../../data/site_pts/all/all_sites_utm_v01.geojson')
    all_sites_wgs84.to_file('../../../data/site_pts/all/all_sites_pts_wgs84_v01.geojson')

    # Saving to shapefile for GEE
    all_sites_utm.to_file('../../../data/site_pts/all/all_sites_utm_v01.shp')
    all_sites_wgs84.to_file('../../../data/site_pts/all/all_sites_pts_wgs84_v01.shp')
