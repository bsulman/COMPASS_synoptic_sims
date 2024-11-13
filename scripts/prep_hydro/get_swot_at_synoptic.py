# https://podaac.github.io/tutorials/notebooks/SearchDownload_SWOTviaCMR.html
import geopandas as gpd
import glob
from pathlib import Path
import pandas as pd
import os
import zipfile
import earthaccess
import json


# Water Mask Pixel Cloud NetCDF - SWOT_L2_HR_PIXC_2.0
# Water Mask Pixel Cloud Vector Attribute NetCDF - SWOT_L2_HR_PIXCVec_2.0
# River Vector Shapefile - SWOT_L2_HR_RiverSP_2.0
# Lake Vector Shapefile - SWOT_L2_HR_LakeSP_2.0
# Raster NetCDF - SWOT_L2_HR_Raster_2.0

#--------------------------------------------------------------------------
# Login:    efluet;   isthis1ANYSAFER
earthaccess.login(strategy='interactive', persist=True)
auth = earthaccess.login()

#--------------------------------------------------------------------------
# Read in SWOT pass/tiles over synoptic sites
swot_tile_df = pd.read_csv('../../data/swot/synoptic_swot_scene.csv')


#--------------------------------------------------------------------------
# Loop through df
for index, row in swot_tile_df.iterrows():
    print(row)
    # Get lake poly
    # download_swot_lakepoly_persite(row)
    # Get PixC vec
    download_swot_pixcvec_persite(row)


#--------------------------------------------------------------------------
#  GET LAKE_SP

def download_swot_lakepoly_persite(x):

    #  Only need pass and tile, not scene
    # C = Cycle;  P = Pass; T=Tile
    granule_search = '*_' + str(row.swot_pass) + '_' + '*NA*'


    results = (
        earthaccess.search_data(
            short_name = 'SWOT_L2_HR_LakeSP_2.0',
            granule_name = granule_search,
            count = 150,
            temporal = ('2023-01-01 00:00:00', '2024-11-29 23:59:59')))


    #--------------------------------------------------------------------------
    # Save results to json file
    with open('../../data/swot/swot_lakesp_search.json', 'w') as f:
        json.dump(results, f, indent=4)


    # Download last item to folder
    earthaccess.download(results[-1], "../../data/swot/lakepoly/")






#--------------------------------------------------------------------------
def download_swot_pixcvec_persite(row):

    #  Only need pass and tile, not scene
    # C = Cycle;  P = Pass; T=Tile
    granule_search = '*_' + str(row.swot_pass) + '_' + str(row.swot_tile) + str(row.swot_tile_l) + '*'

    results = (
        earthaccess.search_data(
            short_name = 'SWOT_L2_HR_PIXC_2.0',
            granule_name = granule_search,
            count = 50,
            temporal = ('2023-01-01 00:00:00', '2024-11-29 23:59:59')))

    # Get list of granules
    granules = [item["umm"]["GranuleUR"] for item in results]

    # Save search results to file
    with open('../../output/results/swot/swot_pixcvec_search.json', 'w') as f:
        json.dump(results, f, indent=4)

    # DOWNLOAD DATA
    earthaccess.download(results[-1], "../../data/swot/pixc_vec/")



#--------------------------------------------------------------------------
# UNZIP
from pathlib import Path
folder = Path("../../data/swot/poly/")
for item in os.listdir(folder): # loop through items in dir
    if item.endswith(".zip"): # check for ".zip" extension
        zip_ref = zipfile.ZipFile(f"{folder}/{item}") # create zipfile object
        zip_ref.extractall(folder) # extract file to dir
        zip_ref.close() # close file

os.listdir(folder)

#--------------------------------------------------------------------------
# here we filter by Reach files (not node), pass=013, continent code=NA
# loop through synoptic sites
synoptic_bbox = \
    (pd.read_csv('../data/raw/transect_coords/compass_synoptic.csv')
    .assign(site_cat = 'synoptic')
    # Group per site
    .groupby(['site_id', 'site_name'])
    # Get bounding box coordinates per site
    .agg(lat_min = ('lat', 'min'),
          lat_max = ('lat', 'max'),
          long_min=('long', 'min'),
          long_max=('long', 'max')
          )
     .reset_index()
     # .applymap(str)
     # .assign(bbox = lambda x: x.min_lat + ' ' + x.max_lat)
     )

synoptic_bbox.head()

#------------------------------------------------------------------
# Function searching and downloading data from bbox coordinates
def download_swot_poly_persite(x):

    # x = df.copy() #synoptic_bbox[1:2]
    # x.info()
    # print(x.long_min)

    results = earthaccess.search_data(
        short_name = 'SWOT_L2_HR_LakeSP_2.0',
        # version = '006',
        # cloud_hosted = True,
        bounding_box=(x.long_min, x.lat_min, x.long_max, x.lat_max),
        # bounding_box = (x.long_min.iloc[0], x.lat_min.iloc[0], x.long_max.iloc[0], x.lat_max.iloc[0]),
        # bounding_box = ( -97, 32.5, -96.5, 33),
        temporal = ('2022-03-01','2024-08-02'),
        count = 100,
        granule_name='*_NA*'  # here we filter by Reach files (not node), pass=013, continent code=NA
        # granule_name = '*Reach*_013_NA*') # here we filter by Reach files (not node), pass=013, continent code=NA
    )

    print(results)
    results = results[0:1]


    # DOWNLOAD DATA
    earthaccess.download(results, "../../data/swot/poly/")

    # UNZIP
    from pathlib import Path
    folder = Path("../../data/swot/poly/")
    for item in os.listdir(folder): # loop through items in dir
        if item.endswith(".zip"): # check for ".zip" extension
            zip_ref = zipfile.ZipFile(f"{folder}/{item}") # create zipfile object
            zip_ref.extractall(folder) # extract file to dir
            zip_ref.close() # close file

    os.listdir(folder)





# Command line query to podaac
# https://podaac.github.io/tutorials/quarto_text/DataSubscriberDownloader.html

# '*453_228*', # '*004_353_264R*',
#  + str(row.swot_scene) + '*'
# granule_name = '*NA*'))  #'*' + str(row.swot_pass) + '_' + str(row.swot_tile) + '*' ))
