import xarray,pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Set up an ELM domain for seven sites across 2 regions x 3 points (upland, transition, wetland)

synoptic = \
    (pd.read_csv('../data/raw/transect_coords/compass_synoptic.csv')
    .assign(grid_points = lambda x: x.site_id + '_' + x.zone_id)
    .assign(site_cat = 'synoptic')
    .drop(columns=['distance'])
     )

# For now we are setting up each land cover type as a separate grid cell. 
# In the future we could do some of this using topo units within grid cells

# Hydrology uses the coastal wetland configuration setup for specifying a time series of hydrological boundary condition
# Hourly time series, just do one year and the model will repeat it. Currently using water level of zero. 
# Surface data set below will define ground surface height above drainage to give different hydrological conditions
# Two grid cells (trough and high centered polygon)
grid_points=synoptic['grid_points']
num_grids=len(grid_points)

elevations=pd.read_csv('../data/synoptic_elev_zone_v3.csv')

if __name__ == '__main__':
    gw=pd.read_csv('../../Data/synoptic_gw_elev_v4.csv',parse_dates=['TIMESTAMP_hourly'],index_col=['site_id','zone_id','TIMESTAMP_hourly'])
    obs_waterlevel=gw['wl_below_surface_m']
    obs_salinity=gw['gw_salinity']

    # Will need to extend to whole years and gap fill. If we backfill beginning and end, we can do 2022-2024 (3 full years gap filled)
    ntimes=365*24*(obs_waterlevel.reset_index()['TIMESTAMP_hourly'].max().year-obs_waterlevel.reset_index()['TIMESTAMP_hourly'].min().year+1)

    tide_data_multicell=xarray.Dataset(
        data_vars={'tide_height':xarray.Variable(('time','gridcell'),data=np.zeros((ntimes,num_grids))+np.nan,attrs={'units':'m'}),
                'tide_salinity':xarray.Variable(('time','gridcell'),data=np.zeros((ntimes,num_grids))+np.nan,attrs={'units':'ppt'}),
                # Setting nonzero nitrate so leaching doesn't become a problem
                'tide_nitrate':xarray.Variable(('time','gridcell'),data=np.zeros((ntimes,num_grids))+0.3e-3,attrs={'units':'mol/L'}),
                },
        coords   ={'time':xarray.Variable(('time',),data=np.arange(ntimes),attrs={'units':'hours'}),
                    'gridcell':np.arange(num_grids)},
        attrs    ={'Description':'Hydrological boundary conditions for grid cells'}
    )


    for sitenum in range(len(grid_points)):
        if (synoptic['site_id'][sitenum],synoptic['zone_id'][sitenum]) in obs_waterlevel and obs_waterlevel[(synoptic['site_id'][sitenum],synoptic['zone_id'][sitenum])].any():
            dt=obs_waterlevel[synoptic['site_id'][sitenum],synoptic['zone_id'][sitenum]].index-obs_waterlevel.reset_index()['TIMESTAMP_hourly'].min()
            t_inds=dt.total_seconds().astype(int)//3600
            tide_data_multicell['tide_height'][t_inds,sitenum]=obs_waterlevel[synoptic['site_id'][sitenum],synoptic['zone_id'][sitenum]]
            tide_data_multicell['tide_salinity'][t_inds,sitenum]=obs_salinity[synoptic['site_id'][sitenum],synoptic['zone_id'][sitenum]]
        elif synoptic['zone_id'][sitenum]=='UP' and (synoptic['site_id'][sitenum],'TR') in obs_waterlevel:
            dt=obs_waterlevel[synoptic['site_id'][sitenum],'TR'].index-plt.matplotlib.dates.datetime.datetime(2022,1,1)
            tide_data_multicell['tide_height'][t_inds,sitenum]=obs_waterlevel[synoptic['site_id'][sitenum],'TR']-(elevations['elev'][sitenum]-elevations['elev'][sitenum-1])
            tide_data_multicell['tide_salinity'][t_inds,sitenum]=obs_salinity[synoptic['site_id'][sitenum],'TR']
            print(f'{(synoptic['site_id'][sitenum],synoptic['zone_id'][sitenum])} not in obs_waterlevel. Using adjusted TR water level')
        else:
            print(f'{(synoptic['site_id'][sitenum],synoptic['zone_id'][sitenum])} not in obs_waterlevel')
            continue

    # Remove unrealistic salinity (only occurs in PTR)
    tide_data_multicell['tide_salinity']=tide_data_multicell['tide_salinity'].where((tide_data_multicell['tide_salinity']<=32)&(tide_data_multicell['tide_salinity']>0.002))
    # Remove spikes
    tide_data_multicell['tide_height'][1:,:]=tide_data_multicell['tide_height'][1:,:].where(abs(tide_data_multicell['tide_height'].diff(dim='time'))<0.5)
    
    # Gap fill with interpolation
    # To do: Make a figure and stats for how much gap filling we did
    for sitenum in range(len(grid_points)):
        start=tide_data_multicell['tide_height'].isel(gridcell=sitenum).dropna(dim='time')['time'][0].item()
        end=tide_data_multicell['tide_height'].isel(gridcell=sitenum).dropna(dim='time')['time'][-1].item()
        tide_data_multicell['tide_height'][start:end,sitenum] = tide_data_multicell['tide_height'][start:end,sitenum].interpolate_na(dim='time',max_gap=5000,method='spline')
        start=tide_data_multicell['tide_salinity'].isel(gridcell=sitenum).dropna(dim='time')['time'][0].item()
        end=tide_data_multicell['tide_salinity'].isel(gridcell=sitenum).dropna(dim='time')['time'][-1].item()
        tide_data_multicell['tide_salinity'][start:end,sitenum] = tide_data_multicell['tide_salinity'][start:end,sitenum].interpolate_na(dim='time',max_gap=5000,method='spline')

        # Fill big gaps with next closest transect point?
        if synoptic['zone_id'][sitenum]=='W':
            # Fill wetland with transition
            tide_data_multicell['tide_height'][:,sitenum]=tide_data_multicell['tide_height'].isel(gridcell=sitenum).fillna(tide_data_multicell['tide_height'].isel(gridcell=sitenum+1)+(tide_data_multicell['tide_height'].isel(gridcell=sitenum).mean()-tide_data_multicell['tide_height'].isel(gridcell=sitenum+1).mean()))
        if synoptic['zone_id'][sitenum]=='TR':
            # Fill transition with wetland
            tide_data_multicell['tide_height'][:,sitenum]=tide_data_multicell['tide_height'].isel(gridcell=sitenum).fillna(tide_data_multicell['tide_height'].isel(gridcell=sitenum-1)+(tide_data_multicell['tide_height'].isel(gridcell=sitenum).mean()-tide_data_multicell['tide_height'].isel(gridcell=sitenum-1).mean()))
        if synoptic['zone_id'][sitenum]=='UP':
            # Fill upland with transition
            tide_data_multicell['tide_height'][:,sitenum]=tide_data_multicell['tide_height'].isel(gridcell=sitenum).fillna(tide_data_multicell['tide_height'].isel(gridcell=sitenum-1)+(tide_data_multicell['tide_height'].isel(gridcell=sitenum).mean()-tide_data_multicell['tide_height'].isel(gridcell=sitenum-1).mean()))

    # Then with ensemble average
    tide_data_multicell['tide_height']=tide_data_multicell['tide_height'].fillna(np.concat([tide_data_multicell['tide_height'].groupby(tide_data_multicell['time']%(365*24)).mean(skipna=True)]*5))
    tide_data_multicell['tide_salinity']=tide_data_multicell['tide_salinity'].fillna(np.concat([tide_data_multicell['tide_salinity'].groupby(tide_data_multicell['time']%(365*24)).mean(skipna=True)]*5))

    # Still some nulls remaining in OWC salinity after all this
    tide_data_multicell['tide_salinity'] = tide_data_multicell['tide_salinity'].interpolate_na(dim='time',max_gap=None,method='spline')

    f,a=plt.subplots(num='Forcing',nrows=2,ncols=7,clear=True)
    for sitenum in range(len(grid_points)):
        tide_data_multicell['tide_height'].isel(gridcell=sitenum).plot(ax=a[0,sitenum//3],label=synoptic['zone_id'][sitenum])
        a[0,sitenum//3].set_title(synoptic['site_id'][sitenum])
        tide_data_multicell['tide_salinity'].isel(gridcell=sitenum).plot(ax=a[1,sitenum//3],label=synoptic['zone_id'][sitenum])
        a[1,sitenum//3].set_title(synoptic['site_id'][sitenum])
    a[0,0].legend()


    

        # if (synoptic['zone_id'][sitenum]=='UP') and t_inds[0]>8760:
        #     tide_data_multicell['tide_height'][0:t_inds[0],sitenum] = tide_data_multicell['tide_height'][:,sitenum].mean()
        # else:
        #     tide_data_multicell['tide_height'][0:t_inds[0],sitenum] = tide_data_multicell['tide_height'][365*24:365*24+t_inds[0],sitenum].values
        

    # f,a=plt.subplots(nrows=2,num='Tide forcing',clear=True)
    # for n,site in enumerate(grid_points):
    #     tide_data_multicell['tide_height'].isel(gridcell=n).plot(ax=a[0],label=site)
    #     tide_data_multicell['tide_salinity'].isel(gridcell=n).plot(ax=a[1],label=site)
    # a[0].legend()

    # Make new multi-grid cell configuration. Treating each land cover type as a separate grid cell
    # This is easier for setting up tidal forcing, but won't work in a larger scale simulation where grid cells need to be spatially defined
    # Long term solution is to use topo units, but will need to figure a way to do hydro forcing in that framework
    # Here we start from the single grid cell configuration for the site and then multiply it into multiple grid cells

    # Ran this on baseline: 
    # python makepointdata.py --point_list ../../COMPASS_synoptic_sims/data/raw/transect_coords/compass_synoptic2.txt --nopftdyn --point_area_kmxkm 0.1 --ccsm_input=/gpfs/wolf2/cades/cli185/world-shared/e3sm/inputdata --keep_duplicates
    domain_multicell=xarray.open_dataset('../surface_data/domain_synoptic_OLMT.nc')
    surfdata_multicell=xarray.open_dataset('../surface_data/surfdata_synoptic_OLMT.nc')

    # for n,site_point in enumerate(grid_points):
    #     site,point=site_point.split('_')
    #     lat=synoptic['lat'][n].astype(float).item()
    #     lon=synoptic['long'][n].astype(float).item()
    #     domain_multicell['yc'][0,n]=lat
    #     if lon>0:
    #         domain_multicell['xc'][0,n]=lon
    #     else:
    #         domain_multicell['xc'][0,n]=lon+360

    # domain_multicell['xv'][0,:,[0,2]] =  domain_multicell['xc'].T.squeeze() + cell_width/2
    # domain_multicell['xv'][0,:,[1,3]] =  domain_multicell['xc'].T.squeeze() - cell_width/2
    # domain_multicell['yv'][0,:,[0,2]] =  domain_multicell['yc'].T.squeeze() + cell_width/2
    # domain_multicell['yv'][0,:,[1,3]] =  domain_multicell['yc'].T.squeeze() - cell_width/2

    # surfdata_multicell['LONGXY'][:]=domain_multicell['xc'].values
    # surfdata_multicell['LATIXY'][:]=domain_multicell['yc'].values

    surfdata_multicell['ht_above_stream'] = surfdata_multicell['TOPO']*0.0 # Set at zero since water levels are being supplied relative to surface
    surfdata_multicell['dist_from_stream'] = surfdata_multicell['ht_above_stream']*0.0+1.0
    # OWC and SWH upland water levels are not in the data so let's just ignore them
    surfdata_multicell['dist_from_stream'][list(grid_points).index('OWC_UP')] = 100.0
    surfdata_multicell['dist_from_stream'][list(grid_points).index('SWH_UP')] = 100.0
    # Model water balance issue with CRC upland
    surfdata_multicell['dist_from_stream'][list(grid_points).index('CRC_UP')] = 50.0


    # We can change soil texture including organic content which is important for hydrological and thermal properties
    # that contribute to active layer thickness
    ## Reminder to look through soil data that people compiled for this!
    kaizad_soildata=pd.read_csv('../../Data/cmps-soil_characterization/1-data/processed/chemistry_combined_all_horizons.csv')
    OMfrac=kaizad_soildata.groupby(['name','site','transect','horizon'])['value'].mean().loc['percentOM'].rename({'upland':'UP','transition':'TR','wetland':'W'})/100
    mod_depths=xarray.open_dataset('../../model_results/COMPASS_synoptic_US-GC3_ICB20TRCNRDCTCBC.elm.h0.1990-01-01-00000.nc')['levdcmp']
    organic_max=130.0
    def find_depthpoint(z):
        return abs(mod_depths-z).argmin().item()
    # Don't have depth data yet so I'm just going to assume O is 5 cm and A is 10 cm and B is 20 cm
    for sitenum in range(len(grid_points)):
        if (synoptic['site_id'][sitenum],synoptic['zone_id'][sitenum]) in OMfrac:
            depth=0.0
            if 'O' in OMfrac[ (synoptic['site_id'][sitenum],synoptic['zone_id'][sitenum])]:
                surfdata_multicell['ORGANIC'][0:find_depthpoint(0.05),sitenum]=organic_max*OMfrac[ (synoptic['site_id'][sitenum],synoptic['zone_id'][sitenum],'O')]
                depth=0.05
                print((synoptic['site_id'][sitenum],synoptic['zone_id'][sitenum],'O'))
            if 'A' in OMfrac[ (synoptic['site_id'][sitenum],synoptic['zone_id'][sitenum])]:
                d1=find_depthpoint(depth)
                d2=find_depthpoint(depth+0.1)
                surfdata_multicell['ORGANIC'][d1:d2,sitenum]=organic_max*OMfrac[ (synoptic['site_id'][sitenum],synoptic['zone_id'][sitenum],'A')]
                depth=depth+0.1
                print((synoptic['site_id'][sitenum],synoptic['zone_id'][sitenum],'A'))
            if 'B' in OMfrac[ (synoptic['site_id'][sitenum],synoptic['zone_id'][sitenum])]:
                d1=find_depthpoint(depth)
                d2=find_depthpoint(depth+0.2)
                surfdata_multicell['ORGANIC'][d1:d2,sitenum]=organic_max*OMfrac[ (synoptic['site_id'][sitenum],synoptic['zone_id'][sitenum],'B')]
                depth=depth+0.2
                print((synoptic['site_id'][sitenum],synoptic['zone_id'][sitenum],'B'))
    # surfdata_multicell['ORGANIC'][...] = surfdata_multicell['ORGANIC'][...]*3.0
    # surfdata_multicell['PCT_SAND'][...] = 75.0
    # surfdata_multicell['PCT_CLAY'][...] = 15.0
    # fdrain controls the relationship between water table depth and topographic drainage
    surfdata_multicell['fdrain']=surfdata_multicell['dist_from_stream']*0.0 + 2.5

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
        pointdata=synoptic.iloc[n]

        surfdata_multicell['PCT_NAT_PFT'][:,n]=0.0
        surfdata_multicell['PCT_NAT_PFT'][pftnames.index('needleleaf_evergreen_temperate_tree'),n]=pointdata['NET_temperate'].item()
        surfdata_multicell['PCT_NAT_PFT'][pftnames.index('broadleaf_evergreen_temperate_tree'),n]=pointdata['BET_temperate'].item()
        surfdata_multicell['PCT_NAT_PFT'][pftnames.index('broadleaf_deciduous_temperate_tree'),n]=pointdata['BDT_temperate'].item()
        surfdata_multicell['PCT_NAT_PFT'][pftnames.index('broadleaf_evergreen_shrub'),n]=pointdata['BES_temperate'].item()
        surfdata_multicell['PCT_NAT_PFT'][pftnames.index('broadleaf_deciduous_temperate_shrub'),n]=pointdata['BDS_temperate'].item()
        surfdata_multicell['PCT_NAT_PFT'][pftnames.index('c3_non-arctic_grass'),n]=pointdata['C3_grass'].item()
        surfdata_multicell['PCT_NAT_PFT'][pftnames.index('c4_grass'),n]=pointdata['C4_grass'].item()

    # surfdata_multicell['PCT_NAT_PFT'] = surfdata_multicell['PCT_NAT_PFT'].round(3)
    # surfdata_multicell['PCT_NAT_PFT'][surfdata_multicell['PCT_NAT_PFT'].argmax(dim='natpft'),:] = surfdata_multicell['PCT_NAT_PFT'][surfdata_multicell['PCT_NAT_PFT'].argmax(dim='natpft'),:] + surfdata_multicell['PCT_NAT_PFT'].sum(dim='natpft')-100

    # PFT percents are required to sum to 100 in each grid cell or the model will crash
    if (surfdata_multicell['PCT_NAT_PFT'].sum(dim='natpft')!=100).any():
        raise ValueError('PFTs do not all add up to 100')

    # Model crashes if mxsoil_color is an array and not an integer
    surfdata_multicell['mxsoil_color']=surfdata_multicell['mxsoil_color'][0]
    surfdata_multicell['mxsoil_order']=surfdata_multicell['mxsoil_order'][0]

    tide_data_multicell.to_netcdf('COMPASS_hydro_BC_fromgw.nc')
    surfdata_multicell.to_netcdf('COMPASS_surfdata_fromgw.nc')
    domain_multicell.to_netcdf('COMPASS_domain_multicell_fromgw.nc')
