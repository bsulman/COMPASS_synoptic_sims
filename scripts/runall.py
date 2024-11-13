

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

# TODO:  Check where zone v3 gets saved;  where is latest elev script?
'prep_points/prep_site_coords.py'

# Make Synoptic+EXCHANGE points from coordinates
# prep_pts


#---------------------------------------------
# PREP DISTANCE FROM PERMANENT WATERBODY




#---------------------------------------------
# PREP WATER LEVEL & SALINITY

# Prep hydro tidal forcing
'prep_hydro/prep_hydro_forcing.py'

# Prep transect groundwater wells
'prep_hydro/prep_gw_depth.py'

# Gapfill hydro forcings
'prep_hydro/gapfill_hydro_forcing.py'

# Fix forcings
'prep_hydro/fix_hydro_forcing.py'




# TODO: verify elevation of points
# TODO: Convert everything to local time (or all GMT?)


#---------------------------------------------
# FORMAT FORCING FOR ELM

# Plot
'plot/ploy_buoy_forcing.py'


# plot heatmap
# plot elev transect
# Prep kmz
# 'get_kmz_synoptic.py'

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

pd.set_option('display.max_rows', 100)

# print cwd
os.getcwd()


#---------------------------------------------
# PREP POINTS & TRANSECTS


#---------------------------------------------
# PREP POINTS of transects



#---------------------------------------------
# PREP ELEVATION

# Make Synoptic+EXCHANGE points from coordinates
# prep_pts



# Prep kmz
# 'get_kmz_synoptic.py'

#---------------------------------------------
# PREP WATER LEVEL





#---------------------------------------------
# PREP SALINITY

# plot heatmap

# plot elev transect


#%% MAKE COMPASS ELM FORCINGS
# Finally - update forcings
