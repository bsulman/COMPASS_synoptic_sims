
#$$$$$$$$$$$$$$$$$$$
#%% Surface data
# TODO: also read in landuse_onecol array (efluet deleted the commented line)
# Read in NCDF array of synoptic transect domain, containing gricell area, fraction, mask and pixel coordinates.
# TODO: Check if/how to update the fractions (currently from ORCHIDEE?); from Wei's transect?


# domain_threecol=xarray.open_dataset('surface_data/domain_3col.nc')
# surfdata_threecol=xarray.open_dataset('surface_data/surfdata_3col.nc')
surfdata_onecol = xr.open_dataset('surface_data/surfdata_1x1pt_US-GC_TransTEMPEST_c20230901.nc')
landuse_onecol = xr.open_dataset(f'/nfs/data/ccsi/proj-shared/E3SM/pt-e3sm-inputdata/atm/datm7/GSWP3_daymet/cpl_bypass_{site}/surfdata.pftdyn.nc')


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




#!!!!!!!!!!!!!!!!!!!!!!!!
#!$$$$$$$$$$$$$$$$$$$$$$

# Threecol is 3 points along transect, multiplying by number of sites for sites x 3 total points
domain_multicell = xarray.concat([domain_threecol] * len(sites), dim='ni')
# Assume all grid cells are the same size.
cell_width = 0.02

for n, site_point in enumerate(grid_points):
    site, point = site_point.split('_')
    lat = site_data[(site_data['site'] == site) & (site_data['zone'] == point)]['lat'].astype(float).item()
    lon = site_data[(site_data['site'] == site) & (site_data['zone'] == point)]['long'].astype(float).item()
    domain_multicell['yc'][0, n] = lat
    if lon > 0:
        domain_multicell['xc'][0, n] = lon
    else:
        domain_multicell['xc'][0, n] = lon + 360

domain_multicell['xv'][0, :, [0, 2]] = domain_multicell['xc'].T.squeeze() + cell_width / 2
domain_multicell['xv'][0, :, [1, 3]] = domain_multicell['xc'].T.squeeze() - cell_width / 2
domain_multicell['yv'][0, :, [0, 2]] = domain_multicell['yc'].T.squeeze() + cell_width / 2
domain_multicell['yv'][0, :, [1, 3]] = domain_multicell['yc'].T.squeeze() - cell_width / 2

surfdata_multicell = xarray.concat([surfdata_onecol] * len(sites) * 3, dim='lsmlon', data_vars='minimal')
surfdata_multicell['LONGXY'][:] = domain_multicell['xc'].values
surfdata_multicell['LATIXY'][:] = domain_multicell['yc'].values
surfdata_multicell['ht_above_stream'] = surfdata_multicell['TOPO']
surfdata_multicell['dist_from_stream'] = surfdata_multicell['ht_above_stream'] * 0.0

# Add new surface data fields specific to gridded hydrological forcing
# Let's define land surface heights relative to the trough
# ht_above_stream in meters units
elevs = site_data['elevation']
elevs = elevs.where((site_data['zone'] == 'Wetland') & (elevs.isna()), -5.0)

for n, site_point in enumerate(grid_points):
    site, point = site_point.split('_')
    surfdata_multicell['ht_above_stream'].squeeze()[n] = \
    site_data[(site_data['site'] == site) & (site_data['zone'] == point)]['elevation'].item()
    surfdata_multicell['dist_from_stream'].squeeze()[n] = \
    site_data[(site_data['site'] == site) & (site_data['zone'] == point)]['distance'].item()

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
surfdata_multicell['fdrain'] = surfdata_multicell['dist_from_stream'] * 0.0 + 5.0

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
    "irrigated_soybean                       "]
            ]

for n, site_point in enumerate(grid_points):
    site, point = site_point.split('_')
    pointdata = site_data[(site_data['site'] == site) & (site_data['zone'] == point)]

    surfdata_multicell['PCT_NAT_PFT'].squeeze()[:, n] = 0.0
    surfdata_multicell['PCT_NAT_PFT'].squeeze()[pftnames.index('needleleaf_evergreen_temperate_tree'), n] = pointdata[
        'NET_temperate'].item()
    surfdata_multicell['PCT_NAT_PFT'].squeeze()[pftnames.index('broadleaf_deciduous_temperate_tree'), n] = pointdata[
        'BDT_temperate'].item()
    surfdata_multicell['PCT_NAT_PFT'].squeeze()[pftnames.index('broadleaf_evergreen_shrub'), n] = pointdata[
        'BES_temperate'].item()
    surfdata_multicell['PCT_NAT_PFT'].squeeze()[pftnames.index('broadleaf_deciduous_temperate_shrub'), n] = pointdata[
        'BDS_temperate'].item()
    surfdata_multicell['PCT_NAT_PFT'].squeeze()[pftnames.index('c3_non-arctic_grass'), n] = pointdata['C3_grass'].item()
    surfdata_multicell['PCT_NAT_PFT'].squeeze()[pftnames.index('c4_grass'), n] = pointdata['C4_grass'].item()

# PFT percents are required to sum to 100 in each grid cell or the model will crash
if (surfdata_multicell['PCT_NAT_PFT'].sum(dim='natpft') != 100).any():
    raise ValueError('PFTs do not all add up to 100')

tide_data_multicell.to_netcdf('COMPASS_hydro_BC_multicell.nc')
surfdata_multicell.to_netcdf('COMPASS_surfdata_multicell.nc')
domain_multicell.to_netcdf('COMPASS_domain_multicell.nc')

import matplotlib.pyplot as plt

f, a = plt.subplots(num='Water heights', clear=True, nrows=2)
a[0].plot(np.arange(len(grid_points)), surfdata_multicell['ht_above_stream'].squeeze(), ls='-', lw=5.0, color='brown',
          label='Soil surface', drawstyle='steps-mid')
a[0].plot(np.arange(len(grid_points)), tide_data_multicell['tide_height'].mean(dim='time'), color='b', alpha=0.5,
          lw=2.0, label='Mean water level', drawstyle='steps-mid')
# a.axhline(tide_data_multicell['tide_height'].quantile(0.9),color='b',alpha=0.5,ls='--',label='90th percentile water level')
# a.axhline(tide_data_multicell['tide_height'].quantile(0.1),color='b',alpha=0.5,ls='--',label='10th percentile water level')
a[0].fill_between(np.arange(len(grid_points)), tide_data_multicell['tide_height'].quantile(0.1, dim='time'),
                  tide_data_multicell['tide_height'].quantile(0.9, dim='time'), color='b', alpha=0.5,
                  label='Water level', step='mid')

a[0].set_ylabel('Height (m)')
a[0].set(xlim=(0., len(grid_points) - 1.0), title='Site elevations')
# a.legend()

bottom = np.zeros(len(grid_points))
pftnum = 0
for pft in range(surfdata_multicell['PCT_NAT_PFT'].shape[0]):
    if surfdata_multicell['PCT_NAT_PFT'][pft, :].any():
        pftfrac = surfdata_multicell['PCT_NAT_PFT'][pft, :].squeeze()
        a[1].bar(np.arange(len(bottom)), pftfrac, bottom=bottom, color='C%d' % pftnum, label=pftnames[pft],
                 align='center')
        bottom = bottom + pftfrac
        pftnum = pftnum + 1
a[1].legend()
a[1].set(xlim=(0., len(grid_points) - 1.0), title='Site vegetation')
a[1].set_xticks(np.arange(len(grid_points)))
a[1].set_xticklabels(grid_points, rotation=90)
a[0].set_xticks([])

f, a = plt.subplots(num='Water time series', nrows=2, clear=True)
a[0].plot(tide_data_multicell['time'] / (24 * 365), tide_data_multicell['tide_height'][:, 0], c='b')
a[0].axhline(surfdata_multicell['ht_above_stream'].squeeze()[0], ls='--', c='C1', lw=4.0, label='Upland')
a[0].axhline(surfdata_multicell['ht_above_stream'].squeeze()[1], ls='--', c='C2', lw=4.0, label='Transition')
a[0].axhline(surfdata_multicell['ht_above_stream'].squeeze()[2], ls='--', c='C3', lw=4.0, label='Wetland')
a[0].set(title='Chesapeake', xlabel='Time (years)', ylabel='Water level (m)')
a[0].legend()

a[1].plot(tide_data_multicell['time'] / (24 * 365), tide_data_multicell['tide_height'][:, -1], c='b')
a[1].axhline(surfdata_multicell['ht_above_stream'].squeeze()[-3], c='C1', ls='--', lw=4.0)
a[1].axhline(surfdata_multicell['ht_above_stream'].squeeze()[-2], c='C2', ls='--', lw=4.0)
a[1].axhline(surfdata_multicell['ht_above_stream'].squeeze()[-1], c='C3', ls='--', lw=4.0)
a[1].set(title='Lake Erie', xlabel='Time (years)', ylabel='Water level (m)')

plt.show()