import xarray,matplotlib.pyplot as plt,pandas as pd,numpy as np

surf=xarray.open_dataset('scripts/COMPASS_surfdata_fromgw.nc')
hydro=xarray.open_dataset('scripts/COMPASS_hydro_BC_fromL2.nc',decode_times=False)

synoptic = \
    (pd.read_csv('data/raw/transect_coords/compass_synoptic.csv')
    .assign(grid_points = lambda x: x.site_id + '_' + x.zone_id)
    .assign(site_cat = 'synoptic')
    .drop(columns=['distance'])
     )
grid_points=list(synoptic['grid_points'])
site_codes={
    'Moneystump':'MSM',
    'Crane Creek':'CRC'
}

params=xarray.open_dataset('surface_data/clm_params.nc',decode_timedelta=False)
pftnames=[name.astype(str).item().strip() for name in params['pftname']]

elevs=pd.read_csv('data/synoptic_elev_zone_v3.csv')

norm=plt.matplotlib.colors.Normalize(vmin=0,vmax=30)
cmap=plt.get_cmap('RdBu_r')

f, a = plt.subplots(num='Water heights', clear=True, nrows=1,ncols=2,squeeze=False,figsize=(13,8))
CB=synoptic[synoptic['region_id']=='CB']
LE=synoptic[synoptic['region_id']=='LE']
for num,site in enumerate(['SWH','GCW','MSM','GWI']):
    for plotnum,pt in enumerate(['W','TR','UP']):
        x=[num*3+plotnum,num*3+plotnum+1]
        elev=elevs['elev'][synoptic['site_id']==site].iloc[plotnum]-elevs['elev'][synoptic['site_id']==site].iloc[0]
        # a[0,1].plot(x, [elevs['elev_fromwetland'][synoptic['site_id']==site].iloc[plotnum]]*2, ls='-', lw=5.0, color='brown',
        #         label='Soil surface')
        a[0,1].add_patch(plt.Rectangle([x[0],0],width=1.0,height=elev,alpha=1.0,edgecolor='k',facecolor='None',zorder=10))
#     a[0,1].plot(x, hydro['tide_height'].mean(dim='time').to_numpy()[synoptic['site_id']==site], color='b', alpha=0.35,
#             lw=2.0, label='Mean water level', drawstyle='steps-mid')

        # a[0,1].fill_between(x, hydro['tide_height'].quantile(0.1, dim='time').to_numpy()[synoptic['site_id']==site][plotnum]+elevs['elev_fromwetland'][synoptic['site_id']==site].iloc[plotnum],
        #             hydro['tide_height'].quantile(0.9, dim='time').to_numpy()[synoptic['site_id']==site][plotnum]+elevs['elev_fromwetland'][synoptic['site_id']==site].iloc[plotnum], alpha=1.0,
        #             label='Water level', step='mid',color=cmap(norm(hydro['tide_salinity'].isel(gridcell=(synoptic['site_id'].to_numpy()==site).nonzero()[0]).isel(gridcell=plotnum).mean())))
        h=hydro['tide_height'].isel(gridcell=(synoptic['site_id'].to_numpy()==site).nonzero()[0]).isel(gridcell=plotnum)+elev
        # bins=np.linspace(h.min().item(),h.max().item(),20)
        bins=np.linspace(-1,4,80)
        hist=h.groupby_bins(bins=bins,group=h).count()
        # a[0,1].plot(hist/hist.sum()*2+x[0]+0.5,bins[1:],drawstyle='steps',c='b')
        a[0,1].barh(bins[1:],hist/hist.max()*0.9,left=x[0],height=bins[1]-bins[0],facecolor=cmap(norm(hydro['tide_salinity'].isel(gridcell=(synoptic['site_id'].to_numpy()==site).nonzero()[0]).isel(gridcell=plotnum).mean())))
    
    a[0,1].axvline(num*3,ls=':',c='k',lw=0.5)
    a[0,1].text((num+0.5)/4,0.98,synoptic['site_name'][synoptic['site_id']==site].iloc[0],rotation=0,fontsize='large',transform=a[0,1].transAxes,ha='center')

a[0,1].set_ylabel('Height (m)',fontsize='large')
a[0,1].set(xlim=(0., len(synoptic[synoptic['region_id']=='CB'])), title='Cheaspeake Bay Site elevations')
a[0,1].set_xticks([])
f.colorbar(ax=a[0,1],mappable=plt.matplotlib.cm.ScalarMappable(cmap=cmap,norm=norm),label='Mean salinity')

for num,site in enumerate(['CRC','PTR','OWC']):
    for plotnum,pt in enumerate(['W','TR','UP']):
        x=[num*3+plotnum,num*3+plotnum+1]
        elev=elevs['elev'][synoptic['site_id']==site].iloc[plotnum]-elevs['elev'][synoptic['site_id']==site].iloc[0]
        # a[0,1].plot(x, [elevs['elev_fromwetland'][synoptic['site_id']==site].iloc[plotnum]]*2, ls='-', lw=5.0, color='brown',
        #         label='Soil surface')
        a[0,0].add_patch(plt.Rectangle([x[0],0],width=1.0,height=elev,alpha=1.0,edgecolor='k',facecolor='None',zorder=10))
#     a[0,1].plot(x, hydro['tide_height'].mean(dim='time').to_numpy()[synoptic['site_id']==site], color='b', alpha=0.35,
#             lw=2.0, label='Mean water level', drawstyle='steps-mid')

        # a[0,0].fill_between(x, hydro['tide_height'].quantile(0.1, dim='time').to_numpy()[synoptic['site_id']==site][plotnum]+elevs['elev_fromwetland'][synoptic['site_id']==site].iloc[plotnum],
        #             hydro['tide_height'].quantile(0.9, dim='time').to_numpy()[synoptic['site_id']==site][plotnum]+elevs['elev_fromwetland'][synoptic['site_id']==site].iloc[plotnum], alpha=1.0,
        #             label='Water level', step='mid',color=cmap(norm(hydro['tide_salinity'].isel(gridcell=(synoptic['site_id'].to_numpy()==site).nonzero()[0]).isel(gridcell=plotnum).mean())))
        h=hydro['tide_height'].isel(gridcell=(synoptic['site_id'].to_numpy()==site).nonzero()[0]).isel(gridcell=plotnum)+elev
        bins=np.linspace(-5,17,100)
        hist=h.groupby_bins(bins=bins,group=h).count()
        a[0,0].barh(bins[1:],hist/hist.max()*0.9,left=x[0],height=bins[1]-bins[0],facecolor=cmap(norm(hydro['tide_salinity'].isel(gridcell=(synoptic['site_id'].to_numpy()==site).nonzero()[0]).isel(gridcell=plotnum).mean())))
    
    a[0,0].axvline(num*3,ls=':',c='k',lw=0.5)
    a[0,0].text((num+0.5)/3,0.98,synoptic['site_name'][synoptic['site_id']==site].iloc[0],rotation=0,fontsize='large',transform=a[0,0].transAxes,ha='center')

a[0,0].set_ylabel('Height (m)',fontsize='large')
a[0,0].set(xlim=(0., len(synoptic[synoptic['region_id']=='LE'])), title='Lake Erie Site elevations')
a[0,0].set_xticks([])
a[0,0].text(6.5,-1,'Wetland',rotation=90,va='top',ha='center',fontsize='large')
a[0,0].text(7.5,-1,'Transition',rotation=90,va='top',ha='center',fontsize='large')
a[0,0].text(8.5,-1,'Upland',rotation=90,va='top',ha='center',fontsize='large')


# bottom = np.zeros(len(synoptic[synoptic['region_id']=='LE']))
# pftnum = 0
# for pft in range(surf['PCT_NAT_PFT'].shape[0]):
#     if surf['PCT_NAT_PFT'][pft, :].any():
#         pftfrac = surf['PCT_NAT_PFT'].squeeze()[pft, synoptic['region_id']=='LE']
#         a[1,1].bar(np.arange(len(bottom)), pftfrac, bottom=bottom, color='C%d' % pftnum, label=pftnames[pft],
#                  align='center')
#         bottom = bottom + pftfrac
#         pftnum = pftnum + 1
# a[1,1].legend()
# a[1,1].set(xlim=(0., len(synoptic[synoptic['region_id']=='LE']) - 1.0), title='Site vegetation')
# a[1,1].set_xticks(np.arange(len(synoptic[synoptic['region_id']=='LE'])))
# a[1,1].set_xticklabels(synoptic['site_name'][synoptic['region_id']=='LE'], rotation=90)
# a[0,1].set_xticks([])