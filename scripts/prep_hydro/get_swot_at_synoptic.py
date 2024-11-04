# https://podaac.github.io/tutorials/notebooks/SearchDownload_SWOTviaCMR.html

import geopandas as gpd
import glob
from pathlib import Path
import pandas as pd
import os
import zipfile
import earthaccess

earthaccess.login(strategy='interactive', persist=True)
# efluet
# isthis1ANYSAFER

auth = earthaccess.login()


# Water Mask Pixel Cloud NetCDF - SWOT_L2_HR_PIXC_2.0
# Water Mask Pixel Cloud Vector Attribute NetCDF - SWOT_L2_HR_PIXCVec_2.0
# River Vector Shapefile - SWOT_L2_HR_RiverSP_2.0
# Lake Vector Shapefile - SWOT_L2_HR_LakeSP_2.0
# Raster NetCDF - SWOT_L2_HR_Raster_2.0


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



#----------------------------------------------

for index, row in synoptic_bbox.iterrows():
    print(index)
    download_swot_poly_persite(row)


# Command line query to podaac
# https://podaac.github.io/tutorials/quarto_text/DataSubscriberDownloader.html
