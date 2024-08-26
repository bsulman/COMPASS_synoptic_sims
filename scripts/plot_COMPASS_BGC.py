import xarray
import matplotlib.pyplot as plt

import sys
sys.path.append('/home/b0u/models/PFLOTRAN/REDOX-PFLOTRAN')
import plot_ELM_alquimia_result as pltELM

yr=1994
COMPASS=xarray.open_dataset(f'/lustre/or-scratch/cades-ccsi/b0u/COMPASS_synoptic_US-GC3_ICB20TRCNRDCTCBC/run/COMPASS_synoptic_US-GC3_ICB20TRCNRDCTCBC.elm.h0.{yr:d}-01-01-00000.nc')

from make_COMPASS_ELM_forcing import grid_points

vars=['VWC','salinity','DOC','FeOxide','Fe2','FeS','Sulfate','Sulfide','pH']
vmax={'salinity':20,'Fe2':2.0,'FeS':90,'sulfate':10.0,'sulfide':10.0,'pH':9.0,'DOC':70,'FeOxide':510}
vmin={'FeOxide':400,'pH':3.0,'salinity':0.0,'sulfide':0.0,'DOC':0.0}
for site in ['SERC','Portage River']:
    f,a=plt.subplots(num=site,clear=True,ncols=4,nrows=len(vars),figsize=(8,12))
    pltELM.plot_vars(COMPASS.isel(lndgrid=grid_points.index(site+'_Wetland')),vars,vmax=vmax,vmin=vmin,a_contour=a[:,0],a_profile=a[:,3],profile_color='blue',mean_profile=True,quantiles=[0.1,0.9],maxdepth=1.0,time_format='%b')
    pltELM.plot_vars(COMPASS.isel(lndgrid=grid_points.index(site+'_Transition')),vars,vmax=vmax,vmin=vmin,a_contour=a[:,1],a_profile=a[:,3],profile_color='purple',mean_profile=True,quantiles=[0.1,0.9],maxdepth=1.0,time_format='%b')
    pltELM.plot_vars(COMPASS.isel(lndgrid=grid_points.index(site+'_Upland')),vars,vmax=vmax,vmin=vmin,a_contour=a[:,2],a_profile=a[:,3],profile_color='red',mean_profile=True,quantiles=[0.1,0.9],maxdepth=1.0,time_format='%b')
    a[0,0].text(0.5,1.5,'Wetland',ha='center',transform=a[0,0].transAxes,fontsize='large')
    a[0,1].text(0.5,1.5,'Transition',ha='center',transform=a[0,1].transAxes,fontsize='large')
    a[0,2].text(0.5,1.5,'Upland',ha='center',transform=a[0,2].transAxes,fontsize='large')
    a[0,3].text(0.5,1.5,'Mean profiles',ha='center',transform=a[0,3].transAxes,fontsize='large')
    a[0,3].legend(handles=a[0,3].lines,labels=['Wetland','Transition','Upland'])
    for ax in a.ravel():
        ax.set_xlabel('')
        ax.title.set_fontsize('medium')

plt.show()