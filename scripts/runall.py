

import pandas as pd
import matplotlib
import os
import numpy as np
import numpy.ma as ma
import pandas as pd
import geopandas as gpd
import fiona
# import rasterstats as rs
from rasterstats import zonal_stats
import rasterio as rio
from matplotlib import pyplot

import rasterstats

import pandas as pd
import xarray as xr

import geopandas as gpd


pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 45)

# print cwd
os.getcwd()

#---------------------------------------------
# PREP POINTS & TRANSECTS
'prep_points/prep_site_coords.py'


#---------------------------------------------
# PREP ELEVATION
# TODO: convert everything to Mean lower low water (MLLW)?

# Make Synoptic+EXCHANGE points from coordinates
# prep_pts

#---------------------------------------------
# PREP WATER LEVEL & SALINITY

# Prep hydro tidal forcing
'prep_hydro/prep_hydro_forcing.py'

# Prep transect groundwater wells
'prep_hydro/prep_gw_depth.py'


# TODO: verify elevation of points
# TODO: Convert everything to local time (or all GMT?)


#---------------------------------------------
# FORMAT FORCING FOR ELM



# plot heatmap
# plot elev transect
# Prep kmz
# 'get_kmz_synoptic.py'