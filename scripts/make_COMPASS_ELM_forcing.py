import xarray as xr
import pandas as pd
import numpy as np
xr.set_options(display_max_rows=10^4) # Increase number of rows printed


# Read in site/zone coordinate file
synoptic = \
    (pd.read_csv('../data/transect_coords/compass_synoptic.csv')
    # Filter to Chesapeake Bay
    .query('region=="Chesapeake Bay"')
    # Concatenate combinations of sites and land cover in a list of strings
    .assign(grid_points = synoptic.site + '_' + synoptic.zone)
    )


# Initially. set up each land cover type as a separate grid cell, but should use using topo units within grid cells in the future.
# TODO: draw in the land cover remote sensing

#%% Hydrology uses the coastal wetland configuration setup for specifying a time series of hydrological boundary condition
# Hourly time series, just do one year and the model will repeat it. Currently using water level of zero. 
# Surface data set below will define ground surface height above drainage to give different hydrological conditions.


#%% Read in hydrological forcings from each site
# TODO: replace these with modules preprocessing the hydro data

# These are different lengths. Erie starts in 1987 but data before that is a harmonic fit Annapolis starts in 1984
Erie_hydro=xr.open_dataset('../data/hydro_forcing/LakeErie_Gageheight_0salt.nc', decode_times=False)
# Annapolis hydro has a short linear gap filling spot in it that we might want to fix
Annapolis_hydro=xr.open_dataset('../data/hydro_forcing/Annapolis_schismPlus2_Peter_salinity_WT6_1_39yrs_NAVD.nc', decode_times=False)


#%% Set hydro forcing array dimension

# Get number of timestep from hydro input
ntimes = len(Annapolis_hydro['time'])
# Set number of grid cells based on number of site x zone combinations (through and high centered polygon)
num_grids = len(synoptic.grid_points)


#%% Create array for hydro forcings
tide_data_multicell = xr.Dataset(
    data_vars={'tide_height': xr.Variable(('time','gridcell'), data=np.zeros((ntimes,num_grids))+0.1,attrs={'units':'m'}),
               'tide_salinity': xr.Variable(('time','gridcell'), data=np.zeros((ntimes,num_grids)),attrs={'units':'ppt'}),
               # Setting nonzero nitrate so leaching doesn't become a problem
               'tide_nitrate':xr.Variable(('time','gridcell'),data=np.zeros((ntimes,num_grids))+0.3e-3,attrs={'units':'mol/L'}),
               },
    coords   ={'time':xr.Variable(('time',),data=np.arange(ntimes),attrs={'units':'hours'}),
                'gridcell':np.arange(num_grids)},
    attrs    ={'Description':'Hydrological boundary conditions for grid cells'}
)


#%% Append hydro, salinity and nitrate variables into an array; set dimensions and metadata
# TODO: Replace data insertion with actual data for both CB and LE regions. Maybe read in individual files one at a time?
for site in synoptic.grid_points:
    if site.split('_')[0] in ['SERC','Sweethall','Goodwin Island','Moneystump']:
        tide_data_multicell['tide_height'][:, grid_points.index(site)]   = np.array(Annapolis_hydro['tide_height'][:,0])
        tide_data_multicell['tide_salinity'][:, grid_points.index(site)] = np.array(Annapolis_hydro['tide_salinity'][:,0])
    else: # If not among Chesapeake region; use Erie forcing (check diff dimensions)
        tide_data_multicell['tide_height'][:,grid_points.index(site)]    = np.array(Erie_hydro['tide_height'][-ntimes:,0])
        tide_data_multicell['tide_salinity'][:,grid_points.index(site)]  = np.array(Erie_hydro['tide_salinity'][-ntimes:,0])



#-----------------------------------------------------------------------------------------------------------------------
#%% DOMAIN  -  Make new multi-grid cell configuration treating each zone as a separate grid cell.
# This is easier for setting up tidal forcing, but won't work in a larger scale simulation where grid cells need to be spatially defined.
# Long term solution is to use topo units, but will need to figure a way to do hydro forcing in that framework.
# Here we start from the single grid cell configuration for the site and then multiply it into multiple grid cells

# Read in NCDF array of synoptic transect domain, containing gricell area, fraction, mask and pixel coordinates.
# TODO: Check if/how to update the fractions (currently from ORCHIDEE?)
domain_threecol = xr.open_dataset('../data/surface_data/domain_3col.nc')
# Repeat identical domain for each site.
domain_multicell = xr.concat([domain_threecol] * synoptic.site.nunique(), dim='ni')

# Set cell size; Assume all grid cells are the same size.
cell_width=0.02

# Copy df to new name
site_coords = synoptic.copy()

# Loop through size-zone rows and modify coordinates of domain_multicell accordingly
for index, row in synoptic.iterrows():
    domain_multicell['xc'][0,index] = row.lat
    if row.long > 0:
        domain_multicell['yc'][0,index] = row.long
    else:
        domain_multicell['yc'][0,index] = row.long + 360

# Modify the domain coordinates
# FIXME: This throws error: "new dimensions ('ni', 'nv') must be a superset of existing dimensions ('ni', 'nj')"
#   Check with Ben S. what is meant to happen
#   dimensions of domain_multicell:  nj = 1 ; ni = 12 ;  nv = 4 ;
domain_multicell['xv'][0,:,[0,2]] = domain_multicell['xc'].T + cell_width/2
domain_multicell['xv'][0,:,[1,3]] = domain_multicell['xc'].T - cell_width/2
domain_multicell['yv'][0,:,[0,2]] = domain_multicell['yc'].T + cell_width/2
domain_multicell['yv'][0,:,[1,3]] = domain_multicell['yc'].T - cell_width/2


#-----------------------------------------------------------------------------------------------------------------------
#%% Surface data
# TODO: also read in landuse_onecol array (efluet deleted the commented line)

# Read in NCDF array of surface data; includes PFT, soil info, per gridcell and depth
surfdata_threecol = xr.open_dataset('../data/surface_data/surfdata_3col.nc')

# Repeat three columns for each site
surfdata_multicell = xr.concat([surfdata_threecol] * synoptic.site.nunique(), dim='gridcell')
surfdata_multicell['LONGXY'] = domain_multicell['xc']
surfdata_multicell['ht_above_stream'] = surfdata_multicell['TOPO']

# Add new surface data fields specific to gridded hydrological forcing
# Land surface heights defined relative to the trough;  ht_above_stream in meters units
# FIXME: Get elevation from actual DEM values
elevs = site_coords['elevation']
elevs = elevs.where((site_coords['zone'] == 'Wetland') & (elevs.isna()), -5.0)

#
for n,site_point in enumerate(grid_points):
    site, point = site_point.split('_')
    surfdata_multicell['ht_above_stream'][n] = site_coords[(site_coords['site']==site) & (site_coords['zone']==point)]['elevation'].item()


# Specify the height of the polygon relative to the "zero" point in the hydrological forcing (in meters)
surfdata_multicell['ht_above_stream'] = surfdata_multicell['TOPO'] - surfdata_multicell['TOPO'][0]

# This should just be distance along the transect
surfdata_multicell['dist_from_stream'] = surfdata_multicell['ht_above_stream'] * 0.0 + 1.0


# We can change soil texture including organic content which is important for hydrological and thermal properties
# that contribute to active layer thickness
# BEO surface data already includes different organic matter percentages
# surfdata_multicell['ORGANIC'][...] = surfdata_multicell['ORGANIC'][...]*3.0
# surfdata_multicell['PCT_SAND'][...] = 75.0
# surfdata_multicell['PCT_CLAY'][...] = 15.0


# fdrain controls the relationship between water table depth and topographic drainage
surfdata_multicell['fdrain'] = surfdata_multicell['dist_from_stream']*0.0 + 5.0


# PFT percents are required to sum to 100 in each grid cell or the model will crash
if (surfdata_multicell['PCT_NAT_PFT'].sum(dim='natpft')!=100).any():
    raise ValueError('PFTs do not all add up to 100')

# Save forcings to NC files
tide_data_multicell.to_netcdf('../data/processed/COMPASS_hydro_BC_multicell.nc')
surfdata_multicell.to_netcdf('../data/processed/COMPASS_surfdata_multicell.nc')
domain_multicell.to_netcdf('../data/processed/COMPASS_domain_multicell.nc')


# /-----------------------------------------------------------#
#/ Plot
import matplotlib.pyplot as plt
f,a=plt.subplots(num='Water heights',clear=True,nrows=1)
a.fill_between(np.arange(len(landcover_types)),np.zeros(len(landcover_types))-.1,surfdata_multicell['ht_above_stream'],ls='-',color='brown',label='Soil surface',step='mid')
a.axhspan(-0.1,tide_data_multicell['tide_height'].mean(),color='b',alpha=0.5,label='Water level')
plt.xticks(ticks=np.arange(len(landcover_types)),labels=landcover_types)
a.set_ylabel('Height (m)')
a.set(xlim=(0,len(landcover_types)-1.5),ylim=(-0.1,0.23),title='Polygon landform levels')
# a.legend()

plt.show()


# TODO: This is not used in script. Why included? Moved to bottom of script to discuss possibly moving to following step.
# Change PFTs to match different ecosystems. This is the list of default ELM PFTs
pftnames = [s.strip() for s in [
  "not_vegetated                           ",
  "needleleaf_evergreen_temperate_tree     ",
  "needleleaf_evergreen_boreal_tree        ",
  "needleleaf_deciduous_boreal_tree        ",
  "broadleaf_evergreen_tropical_tree       ",
  "broadleaf_evergreen_temperate_tree      ",
  "broadleaf_deciduous_tropical_tree       ",
  "broadleaf_deciduous_temperate_tree      ",
  "broadleaf_deciduous_boreal_tree         ",
  "broadleaf_evergreen_shrub               ",
  "broadleaf_deciduous_temperate_shrub     ",
  "broadleaf_deciduous_boreal_shrub        ",
  "c3_arctic_grass                         ",
  "c3_non-arctic_grass                     ",
  "c4_grass                                ",
  "c3_crop                                 ",
  "c3_irrigated                            ",
  "corn                                    ",
  "irrigated_corn                          ",
  "spring_temperate_cereal                 ",
  "irrigated_spring_temperate_cereal       ",
  "winter_temperate_cereal                 ",
  "irrigated_winter_temperate_cereal       ",
  "soybean                                 ",
  "irrigated_soybean                       " ]
]

