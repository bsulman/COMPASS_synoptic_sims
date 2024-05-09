import xarray
import numpy as np
import matplotlib.pyplot as plt

# Set up an ELM domain for seven sites across 2 regions x 3 points (upland, transition, wetland)

landcover_types=[
    'Upland',
    'Transition',
    'Wetland'
]

regions=[
    'Lake Erie',
    'Chesapeake'
]

sites=[
    'SERC',
    'Sweethall',
    'Goodwin Island',
    'Moneystump',
    'Portage River',
    'Old Woman Creek',
    'Crane Creek',
    ]

grid_points=[]
for site in sites:
    for point in landcover_types:
        grid_points.append(site+'_'+point)

# For now we are setting up each land cover type as a separate grid cell. 
# In the future we could do some of this using topo units within grid cells

# Hydrology uses the coastal wetland configuration setup for specifying a time series of hydrological boundary condition
# Hourly time series, just do one year and the model will repeat it. Currently using water level of zero. 
# Surface data set below will define ground surface height above drainage to give different hydrological conditions
# Two grid cells (trough and high centered polygon)
num_grids=len(grid_points)

# These are different lengths. Erie starts in 1987 but data before that is a harmonic fit
# Anapolis starts in 1984
Erie_hydro=xarray.open_dataset('hydro_forcing/LakeErie_Gageheight_0salt.nc',decode_times=False)
# Annapolis hydro has a short linear gap filling spot in it that we might want to fix
Annapolis_hydro=xarray.open_dataset('hydro_forcing/Annapolis_schismPlus2_Peter_salinity_WT6_1_39yrs_NAVD.nc',decode_times=False)

ntimes=len(Annapolis_hydro['time'])
tide_data_multicell=xarray.Dataset(
    data_vars={'tide_height':xarray.Variable(('time','gridcell'),data=np.zeros((ntimes,num_grids))+0.1,attrs={'units':'m'}),
               'tide_salinity':xarray.Variable(('time','gridcell'),data=np.zeros((ntimes,num_grids)),attrs={'units':'ppt'}),
               # Setting nonzero nitrate so leaching doesn't become a problem
               'tide_nitrate':xarray.Variable(('time','gridcell'),data=np.zeros((ntimes,num_grids))+0.3e-3,attrs={'units':'mol/L'}),
               },
    coords   ={'time':xarray.Variable(('time',),data=np.arange(ntimes),attrs={'units':'hours'}),
                'gridcell':np.arange(num_grids)},
    attrs    ={'Description':'Hydrological boundary conditions for grid cells'}
)

for site in grid_points:
    if site.split('_')[0] in ['SERC','Sweethall','Goodwin Island','Moneystump']:
        # Adding 30 cm to Annapolis water level since it seems too low
        tide_data_multicell['tide_height'][:,grid_points.index(site)]=np.array(Annapolis_hydro['tide_height'][:,0])+0.3
        tide_data_multicell['tide_salinity'][:,grid_points.index(site)]=np.array(Annapolis_hydro['tide_salinity'][:,0])
    else:
        tide_data_multicell['tide_height'][:,grid_points.index(site)]=np.array(Erie_hydro['tide_height'][-ntimes:,0])
        tide_data_multicell['tide_salinity'][:,grid_points.index(site)]=np.array(Erie_hydro['tide_salinity'][-ntimes:,0])

# f,a=plt.subplots(nrows=2,num='Tide forcing',clear=True)
# for n,site in enumerate(grid_points):
#     tide_data_multicell['tide_height'].isel(gridcell=n).plot(ax=a[0],label=site)
#     tide_data_multicell['tide_salinity'].isel(gridcell=n).plot(ax=a[1],label=site)
# a[0].legend()

# Make new multi-grid cell configuration. Treating each land cover type as a separate grid cell
# This is easier for setting up tidal forcing, but won't work in a larger scale simulation where grid cells need to be spatially defined
# Long term solution is to use topo units, but will need to figure a way to do hydro forcing in that framework
# Here we start from the single grid cell configuration for the site and then multiply it into multiple grid cells

domain_threecol=xarray.open_dataset('surface_data/domain_3col.nc')
surfdata_threecol=xarray.open_dataset('surface_data/surfdata_3col.nc')
# landuse_onecol=xarray.open_dataset(f'/nfs/data/ccsi/proj-shared/E3SM/pt-e3sm-inputdata/atm/datm7/GSWP3_daymet/cpl_bypass_{site}/surfdata.pftdyn.nc')

# Change this with GPS coordinates for all actual sites
import pandas
site_data=pandas.read_csv('surface_data/COMPASS_sites.csv',na_values=['NA ','NAN']).replace(
    {'gcrew':'SERC',
     'sweethall':'Sweethall',
     'goodwin':'Goodwin Island',
     'moneystump':'Moneystump',
     'ow_creek':'Old Woman Creek',
     'portage_river':'Portage River',
     'crane_creek':'Crane Creek',
     'upland':'Upland','trans':'Transition','wetland':'Wetland'},
     )

domain_multicell=xarray.concat([domain_threecol]*len(sites),dim='ni')
# Assume all grid cells are the same size.
cell_width=0.02

for n,site_point in enumerate(grid_points):
    site,point=site_point.split('_')
    lat=site_data[(site_data['site']==site)&(site_data['zone']==point)]['lat'].astype(float).item()
    lon=site_data[(site_data['site']==site)&(site_data['zone']==point)]['long'].astype(float).item()
    domain_multicell['xc'][0,n]=lat
    if lon>0:
        domain_multicell['yc'][0,n]=lon
    else:
        domain_multicell['yc'][0,n]=lon+360

domain_multicell['xv'][0,:,[0,2]] =  domain_multicell['xc'].T + cell_width/2
domain_multicell['xv'][0,:,[1,3]] =  domain_multicell['xc'].T - cell_width/2
domain_multicell['yv'][0,:,[0,2]] =  domain_multicell['yc'].T + cell_width/2
domain_multicell['yv'][0,:,[1,3]] =  domain_multicell['yc'].T - cell_width/2

surfdata_multicell = xarray.concat([surfdata_threecol]*len(sites),dim='gridcell')
surfdata_multicell['LONGXY']=domain_multicell['xc']
surfdata_multicell['ht_above_stream'] = surfdata_multicell['TOPO']
surfdata_multicell['dist_from_stream'] = surfdata_multicell['ht_above_stream']*0.0

# Add new surface data fields specific to gridded hydrological forcing
# Let's define land surface heights relative to the trough
# ht_above_stream in meters units
elevs=site_data['elevation']
elevs=elevs.where((site_data['zone']=='Wetland')&(elevs.isna()),-5.0)

for n,site_point in enumerate(grid_points):
    site,point=site_point.split('_')
    surfdata_multicell['ht_above_stream'][n]=site_data[(site_data['site']==site)&(site_data['zone']==point)]['elevation'].item()
    surfdata_multicell['dist_from_stream'][n]=site_data[(site_data['site']==site)&(site_data['zone']==point)]['distance'].item()
    

    
# surfdata_multicell['ht_above_stream'] = surfdata_multicell['TOPO']-surfdata_multicell['TOPO'][0]
# Here we specify the height of the polygon relative to the "zero" point in the hydrological forcing (in meters)

# This should just be distance along the transect
# surfdata_multicell['dist_from_stream'] = surfdata_multicell['ht_above_stream']*0.0 + 1.0

# We can change soil texture including organic content which is important for hydrological and thermal properties
# that contribute to active layer thickness
# BEO surface data already includes different organic matter percentages
# surfdata_multicell['ORGANIC'][...] = surfdata_multicell['ORGANIC'][...]*3.0
# surfdata_multicell['PCT_SAND'][...] = 75.0
# surfdata_multicell['PCT_CLAY'][...] = 15.0
# fdrain controls the relationship between water table depth and topographic drainage
surfdata_multicell['fdrain']=surfdata_multicell['dist_from_stream']*0.0 + 5.0

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

for n,site_point in enumerate(grid_points):

    site,point=site_point.split('_')
    pointdata=site_data[(site_data['site']==site)&(site_data['zone']==point)]

    surfdata_multicell['PCT_NAT_PFT'][:,n]=0.0
    surfdata_multicell['PCT_NAT_PFT'][pftnames.index('needleleaf_evergreen_temperate_tree'),n]=pointdata['NET_temperate'].item()
    surfdata_multicell['PCT_NAT_PFT'][pftnames.index('broadleaf_deciduous_temperate_tree'),n]=pointdata['BDT_temperate'].item()
    surfdata_multicell['PCT_NAT_PFT'][pftnames.index('broadleaf_evergreen_shrub'),n]=pointdata['BES_temperate'].item()
    surfdata_multicell['PCT_NAT_PFT'][pftnames.index('broadleaf_deciduous_temperate_shrub'),n]=pointdata['BDS_temperate'].item()
    surfdata_multicell['PCT_NAT_PFT'][pftnames.index('c3_non-arctic_grass'),n]=pointdata['C3_grass'].item()
    surfdata_multicell['PCT_NAT_PFT'][pftnames.index('c4_grass'),n]=pointdata['C4_grass'].item()

    

# PFT percents are required to sum to 100 in each grid cell or the model will crash
if (surfdata_multicell['PCT_NAT_PFT'].sum(dim='natpft')!=100).any():
    raise ValueError('PFTs do not all add up to 100')


tide_data_multicell.to_netcdf('COMPASS_hydro_BC_multicell.nc')
surfdata_multicell.to_netcdf('COMPASS_surfdata_multicell.nc')
domain_multicell.to_netcdf('COMPASS_domain_multicell.nc')

import matplotlib.pyplot as plt
f,a=plt.subplots(num='Water heights',clear=True,nrows=2)
a[0].plot(np.arange(len(grid_points)),surfdata_multicell['ht_above_stream'],ls='-',lw=5.0,color='brown',label='Soil surface',drawstyle='steps-mid')
a[0].plot(np.arange(len(grid_points)),tide_data_multicell['tide_height'].mean(dim='time'),color='b',alpha=0.5,lw=2.0,label='Mean water level',drawstyle='steps-mid')
# a.axhline(tide_data_multicell['tide_height'].quantile(0.9),color='b',alpha=0.5,ls='--',label='90th percentile water level')
# a.axhline(tide_data_multicell['tide_height'].quantile(0.1),color='b',alpha=0.5,ls='--',label='10th percentile water level')
a[0].fill_between(np.arange(len(grid_points)),tide_data_multicell['tide_height'].quantile(0.1,dim='time'),tide_data_multicell['tide_height'].quantile(0.9,dim='time'),color='b',alpha=0.5,label='Water level',step='mid')

a[0].set_ylabel('Height (m)')
a[0].set(xlim=(0.,len(grid_points)-1.0),title='Site elevations')
# a.legend()

bottom=np.zeros(len(grid_points))
pftnum=0
for pft in range(surfdata_multicell['PCT_NAT_PFT'].shape[0]):
    if surfdata_multicell['PCT_NAT_PFT'][pft,:].any():
        pftfrac=surfdata_multicell['PCT_NAT_PFT'][pft,:]
        a[1].bar(np.arange(len(bottom)),pftfrac,bottom=bottom,color='C%d'%pftnum,label=pftnames[pft],align='center')
        bottom=bottom+pftfrac
        pftnum = pftnum + 1
a[1].legend()
a[1].set(xlim=(0.,len(grid_points)-1.0),title='Site vegetation')
a[1].set_xticks(np.arange(len(grid_points)))
a[1].set_xticklabels(grid_points,rotation=90)
a[0].set_xticks([])

f,a=plt.subplots(num='Water time series',nrows=2,clear=True)
a[0].plot(tide_data_multicell['time']/(24*365),tide_data_multicell['tide_height'][:,0],c='b')
a[0].axhline(surfdata_multicell['ht_above_stream'][0],ls='--',c='C1',lw=4.0,label='Upland')
a[0].axhline(surfdata_multicell['ht_above_stream'][1],ls='--',c='C2',lw=4.0,label='Transition')
a[0].axhline(surfdata_multicell['ht_above_stream'][2],ls='--',c='C3',lw=4.0,label='Wetland')
a[0].set(title='Chesapeake',xlabel='Time (years)',ylabel='Water level (m)')
a[0].legend()

a[1].plot(tide_data_multicell['time']/(24*365),tide_data_multicell['tide_height'][:,-1],c='b')
a[1].axhline(surfdata_multicell['ht_above_stream'][-3],c='C1',ls='--',lw=4.0)
a[1].axhline(surfdata_multicell['ht_above_stream'][-2],c='C2',ls='--',lw=4.0)
a[1].axhline(surfdata_multicell['ht_above_stream'][-1],c='C3',ls='--',lw=4.0)
a[1].set(title='Lake Erie',xlabel='Time (years)',ylabel='Water level (m)')


plt.show()