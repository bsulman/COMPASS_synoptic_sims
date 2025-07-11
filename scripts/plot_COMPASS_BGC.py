import xarray
import matplotlib.pyplot as plt

import sys
sys.path.append('/Users/b0u/Documents/REDOX-PFLOTRAN')
import plot_ELM_alquimia_result as pltELM

# yr=1990
# COMPASS=xarray.open_dataset(f'../model_results/COMPASS_synoptic_US-GC3_ICB20TRCNRDCTCBC.elm.h0.{yr:d}-01-01-00000.nc')
COMPASS=xarray.open_dataset('../../COMPASS_synoptic_plothydro_US-GC3_ICB20TRCNRDCTCBC.elm.h0.2024-01-01-00000.nc')

from make_COMPASS_ELM_forcing import grid_points
grid_points=list(grid_points)

vars=['VWC','O2','salinity','DOC']
vars2=['FeOxide','Fe2','FeS']
vars3=['Sulfate','Sulfide','pH']
vmax={'salinity':20,'Fe2':2.0,'FeS':90,'sulfate':10.0,'sulfide':10.0,'pH':9.0,'DOC':70,'FeOxide':510}
vmin={'FeOxide':400,'pH':3.0,'salinity':0.0,'sulfide':0.0,'DOC':0.0}
for site in ['MSM','CRC']:
    for num,varset in enumerate([vars,vars2,vars3]):
        f,a=plt.subplots(num=site+'_%d'%num,clear=True,ncols=4,nrows=len(varset),figsize=(8,6))
        pltELM.plot_vars(COMPASS.isel(lndgrid=grid_points.index(site+'_W')),varset,vmax=vmax,vmin=vmin,a_contour=a[:,0],a_profile=a[:,3],profile_color='blue',mean_profile=True,quantiles=[0.1,0.9],maxdepth=0.45,time_format='%b')
        pltELM.plot_vars(COMPASS.isel(lndgrid=grid_points.index(site+'_TR')),varset,vmax=vmax,vmin=vmin,a_contour=a[:,1],a_profile=a[:,3],profile_color='purple',mean_profile=True,quantiles=[0.1,0.9],maxdepth=0.45,time_format='%b')
        pltELM.plot_vars(COMPASS.isel(lndgrid=grid_points.index(site+'_UP')),varset,vmax=vmax,vmin=vmin,a_contour=a[:,2],a_profile=a[:,3],profile_color='red',mean_profile=True,quantiles=[0.1,0.9],maxdepth=0.45,time_format='%b')
        a[0,0].text(0.5,1.5,'Wetland',ha='center',transform=a[0,0].transAxes,fontsize='large')
        a[0,1].text(0.5,1.5,'Transition',ha='center',transform=a[0,1].transAxes,fontsize='large')
        a[0,2].text(0.5,1.5,'Upland',ha='center',transform=a[0,2].transAxes,fontsize='large')
        a[0,3].text(0.5,1.5,'Mean profiles',ha='center',transform=a[0,3].transAxes,fontsize='large')
        a[0,3].legend(handles=a[0,3].lines,labels=['Wetland','Transition','Upland'])
        for ax in a.ravel():
            ax.set_xlabel('')
            ax.title.set_fontsize('medium')

f,a=plt.subplots(num='hydrology',clear=True,ncols=2)
site='CRC'
pltELM.plot_vars(COMPASS.isel(lndgrid=grid_points.index(site+'_W')),['H2OSFC'],a_contour=a[0],profile_color='blue')
pltELM.plot_vars(COMPASS.isel(lndgrid=grid_points.index(site+'_TR')),['H2OSFC'],a_contour=a[0],profile_color='purple')
pltELM.plot_vars(COMPASS.isel(lndgrid=grid_points.index(site+'_UP')),['H2OSFC'],a_contour=a[0],profile_color='red')
a[0].set_title(site)

site='MSM'
pltELM.plot_vars(COMPASS.isel(lndgrid=grid_points.index(site+'_W')),['H2OSFC'],a_contour=a[1],profile_color='blue')
pltELM.plot_vars(COMPASS.isel(lndgrid=grid_points.index(site+'_TR')),['H2OSFC'],a_contour=a[1],profile_color='purple')
pltELM.plot_vars(COMPASS.isel(lndgrid=grid_points.index(site+'_UP')),['H2OSFC'],a_contour=a[1],profile_color='red')
a[1].set_title(site)

plt.show()