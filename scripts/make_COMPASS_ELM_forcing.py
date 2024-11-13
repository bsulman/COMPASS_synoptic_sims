import xarray as xr
import pandas as pd
import numpy as np
xr.set_options(display_max_rows=10^4)
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 50)


#%%--------------------------------------------------------------------------------------
# SITE COORDS

# Read in site/zone coordinate file
# synoptic = \
    (pd.read_csv('../data/raw/transect_coords/compass_synoptic.csv')
    .assign(grid_points = lambda x: x.site_id + '_' + x.zone_id)
    .assign(site_cat = 'synoptic')
    .drop(columns=['distance'])
     )

# GET DISTANCE FROM NWI PERMANENT WATER BODY
dist = pd.read_csv('../../data/site_pts/synoptic/synoptic_sites_pts_v2_wdist.csv')[['site_id', 'zone', 'distance']]
dist.columns = ['site_name', 'zone_name', 'distance']

# GET ELEVATION
elev = pd.read_csv('../../output/results/elev/synoptic_elev_zone_v3.csv')[['site_name', 'zone_name', 'elev']]

# Join elev and distance to synoptic file
synoptic = \
    (synoptic.merge(dist, on=['site_name', 'zone_name'], how='left')
     .merge(elev, on=['site_name', 'zone_name'], how='left'))


#%%--------------------------------------------------------------------------------------
#  HYDRO
# Hydrology uses the coastal wetland configuration setup for specifying a time series of hydrological boundary condition
# Hourly time series, just do one year and the model will repeat it. Currently using water level of zero.
# These data were compiled, outlier filtered, gapfilled and cut to an identical record period across sites.
hydro_filled_df = (
    pd.read_csv('../../output/results/hydro_forcing_gauges/buoy_wl_all_syn_v4_filled_fixed.csv'))


#%% Set hydro forcing array dimension from hydro input
# Note: Different length will require multiple ELM runs.
ntimes = hydro_filled_df[hydro_filled_df.site_name=='GCReW'].shape[0] # len(Annapolis_hydro['time'])
# Set number of grid cells based on number of site x zone combinations (through and high centered polygon)
num_grids = len(synoptic.grid_points)


#%% Create array for hydro forcings
tide_data_multicell = xr.Dataset(
    data_vars={'tide_height': xr.Variable(('time','gridcell'), data=np.zeros((ntimes,num_grids)),attrs={'units':'m'}),
               'tide_salinity': xr.Variable(('time','gridcell'), data=np.zeros((ntimes,num_grids)),attrs={'units':'ppt'}),
               # Setting nonzero nitrate so leaching doesn't become a problem
               'tide_nitrate':xr.Variable(('time','gridcell'),data=np.zeros((ntimes,num_grids))+0.3e-3,attrs={'units':'mol/L'}),
               },
    coords   ={'time':xr.Variable(('time',), data=np.arange(ntimes),attrs={'units':'hours'}),
               'gridcell':np.arange(num_grids)},
    attrs    ={'Description':'Hydrological boundary conditions for grid cells'}
    )


#%% Append hydro, salinity and nitrate variables into an array; set dimensions and metadata
for index, row in synoptic.iterrows():

    # Get site id, to write into file
    site_id = row.site_id

    # Subset forcing to current site
    hydro_forcing_subset = hydro_filled_df[hydro_filled_df.site_name == row.site_name]

    # Write to xarray
    tide_data_multicell['tide_height'][:, index]  = np.array(hydro_forcing_subset['water_height_m'])
    tide_data_multicell['tide_salinity'][:, index]= np.array(hydro_forcing_subset['water_salinity'])


#--------------------------------------------------------------------------------------
#  MULTI-CELL SURFACE
# Surface data set below will define ground surface height above drainage to give different hydrological conditions.
# Make new multi-grid cell configuration. Treating each land cover type as a separate grid cell
# This is easier for setting up tidal forcing, but won't work in a larger scale simulation where grid cells need to be spatially defined
# Long term solution is to use topo units, but will need to figure a way to do hydro forcing in that framework
# Here we start from the single grid cell configuration for the site and then multiply it into multiple grid cells

domain_threecol  =xr.open_dataset('../data/raw/surface_data/domain_3col.nc')
surfdata_threecol=xr.open_dataset('../data/raw/surface_data/surfdata_3col.nc')
surfdata_onecol  =xr.open_dataset('../data/raw/surface_data/surfdata_1x1pt_US-GC_TransTEMPEST_c20230901.nc')
# landuse_onecol=xarray.open_dataset(f'/nfs/data/ccsi/proj-shared/E3SM/pt-e3sm-inputdata/atm/datm7/GSWP3_daymet/cpl_bypass_{site}/surfdata.pftdyn.nc')
# TODO: NLCD FOR LAND USE

# Threecol is 3 points along transect, multiplying by number of sites for sites x 3 total points
domain_multicell=xr.concat([domain_threecol] * len(synoptic.site_id.unique()),dim='ni')
# Assume all grid cells are the same size.
cell_width=0.02

# Loop through grid-points
for n, row in synoptic.iterrows():
    lat = row.lat
    lon = row.long
    # Write lat to file
    domain_multicell['yc'][0,n]=lat
    # Fix long coordinates to a 0-360deg format
    if lon>0:
        domain_multicell['xc'][0,n]=lon
    else:
        domain_multicell['xc'][0,n]=lon+360
    # Write in elevation and distance
    surfdata_multicell['ht_above_stream'].squeeze()[n] = row.elev
    surfdata_multicell['dist_from_stream'].squeeze()[n] = row.distance

# Modify coordinates
domain_multicell['xv'][0,:,[0,2]] =  domain_multicell['xc'].T.squeeze() + cell_width/2
domain_multicell['xv'][0,:,[1,3]] =  domain_multicell['xc'].T.squeeze() - cell_width/2
domain_multicell['yv'][0,:,[0,2]] =  domain_multicell['yc'].T.squeeze() + cell_width/2
domain_multicell['yv'][0,:,[1,3]] =  domain_multicell['yc'].T.squeeze() - cell_width/2

surfdata_multicell = xr.concat([surfdata_onecol]*len(synoptic.site_id.unique())*3,dim='lsmlon',data_vars='minimal')
surfdata_multicell['LONGXY'][:]=domain_multicell['xc'].values
surfdata_multicell['LATIXY'][:]=domain_multicell['yc'].values
surfdata_multicell['ht_above_stream'] = surfdata_multicell['TOPO']
surfdata_multicell['dist_from_stream'] = surfdata_multicell['ht_above_stream']*0.0


#-----------------------------------------------------------------------------------------------------------------------
# Change PFTs to match different ecosystems. This is the list of default ELM PFTs
pftnames = pd.read_csv('../data/raw/surface_data/elm_pft_names.csv', header=None)#.tolist()
pftnames = pftnames[0].tolist()


for n, row in synoptic.iterrows():
    # site, point = site_point.split('_')
    pointdata = row #site_data[(site_data['site'] == site) & (site_data['zone'] == point)]

    surfdata_multicell['PCT_NAT_PFT'].squeeze()[:, n] = 0.0
    surfdata_multicell['PCT_NAT_PFT'].squeeze()[pftnames.index('needleleaf_evergreen_temperate_tree'), n] = pointdata['NET_temperate']
    surfdata_multicell['PCT_NAT_PFT'].squeeze()[pftnames.index('broadleaf_deciduous_temperate_tree'), n] = pointdata[
        'BDT_temperate']
    surfdata_multicell['PCT_NAT_PFT'].squeeze()[pftnames.index('broadleaf_evergreen_shrub'), n] = pointdata[
        'BES_temperate']
    surfdata_multicell['PCT_NAT_PFT'].squeeze()[pftnames.index('broadleaf_deciduous_temperate_shrub'), n] = pointdata[
        'BDS_temperate']
    surfdata_multicell['PCT_NAT_PFT'].squeeze()[pftnames.index('c3_non-arctic_grass'), n] = pointdata['C3_grass']
    surfdata_multicell['PCT_NAT_PFT'].squeeze()[pftnames.index('c4_grass'), n] = pointdata['C4_grass']

# CHECK sum(PFT)==100%
# PFT percents are required to sum to 100 in each grid cell or the model will crash
if (surfdata_multicell['PCT_NAT_PFT'].sum(dim='natpft') != 100).any():
    raise ValueError('PFTs do not all add up to 100')

# Write to file
tide_data_multicell.to_netcdf('../output/COMPASS_hydro_BC_multicell_v01.nc')
surfdata_multicell.to_netcdf('../output/COMPASS_surfdata_multicell_v01.nc')
domain_multicell.to_netcdf('../output/COMPASS_domain_multicell_v01.nc')


