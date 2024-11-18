

import matplotlib
import os
import numpy as np
import numpy.ma as ma
import pandas as pd
import geopandas as gpd
import fiona
import xarray as xr
# import rasterstats as rs
from rasterstats import zonal_stats
import rasterio as rio
from matplotlib import pyplot
import rasterstats
import importlib


# Increase the number of rows and columns variables printed
pd.set_option('display.max_rows', 50); pd.set_option('display.max_columns', 45)

# Increase the number of rows and variables printed
xr.set_options(display_max_rows=20)#, display_max_columns=20)

# print cwd
os.getcwd()

#---------------------------------------------
# PREP POINTS & TRANSECTS
'prep_points/prep_site_coords.py'


#---------------------------------------------
# PREP ELEVATION
# TODO: convert everything to Mean lower low water (MLLW)?

# TODO:  Check where zone v3 gets saved;  where is latest elev script?

# TODO: Rerun elevation at points; to fix Portage River elevations being inverted when using transect.
'prep_points/prep_site_coords.py'

# Make Synoptic+EXCHANGE points from coordinates
# prep_pts


#---------------------------------------------
# PREP DISTANCE FROM PERMANENT WATERBODY


#---------------------------------------------
# PREP BOUNDARY WATER LEVEL & SALINITY

# TODO: Convert everything to local time (or all GMT?)
# TODO Verify shared datum

# Prep hydro tidal forcing
'prep_hydro/prep_hydro_forcing.py'

# Gapfill hydro forcings
'prep_hydro/gapfill_hydro_forcing.py'

# Fix forcings
'prep_hydro/fix_hydro_forcing.py'


#---------------------------------------------
# PREP SYNOPTIC WELLS

# Prep transect groundwater wells
'prep_hydro/prep_gw_depth.py'


#---------------------------------------------
# FORMAT FORCING FOR ELM

'make_COMPASS_ELM_forcing.py'