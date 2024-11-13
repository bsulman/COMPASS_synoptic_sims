

import pandas as pd

#----------------------------------------------------------------------------------
# Read schism data
schism_dat  = pd.read_csv('../../../output/syn_sites_schism_salininty.csv')
schism_dat['datetime'] = pd.to_datetime(schism_dat['datetime'])
schism_dat['data_source'] = 'SCHISM'
schism_dat = schism_dat[(schism_dat['site_name'] == 'Sweet Hall Marsh')]

#----------------------------------------------------------------------------------
# Read gauges data

def get_gauge_data(directory):
    df= pd.read_csv(directory)
    df['SAMPLE_DATETIME'] = pd.to_datetime(df['SAMPLE_DATETIME'])
    sdate = '2017-01-01'
    df = df[df['SAMPLE_DATETIME'] >= sdate]
    edate = '2018-12-31'
    df = df[df['SAMPLE_DATETIME'] <= edate]
    df['data_source'] = 'Gauge'
    return(df)


df_goodwin = get_gauge_data('../../../output/results/gauges/GoodwinIsland_CH019.38_hourly.csv')
# df_goodwin['STATION'] = 'Goodwin Island'

df_sweethall = get_gauge_data('../../../output/results/gauges/SweetHallMarsh_PMK012.18_hourly.csv')
# df_sweethall['STATION'] = 'Sweet Hall Marsh'


#---------------------------------------------------------------------------------------



#---------------------------------------------------------------------------------------
from plotnine import ggplot, aes, geom_point, scale_x_datetime, labs, theme_bw

import matplotlib
matplotlib.use('agg')

# Plotting with Plotnine
plot = (
    ggplot() +
    geom_point(schism_dat, aes(x='datetime', y='salinity', color='data_source', shape='data_source'), stroke=0.01, fill=None, size=0.75) +
    geom_point(df_sweethall, aes(x='SAMPLE_DATETIME', y='SALINITY', color='data_source', shape='data_source'), stroke=0.01, fill=None, size=0.75) +
    # geom_point(df_goodwin, aes(x='SAMPLE_DATETIME', y='SALINITY', color='STATION', shape='data_source'), stroke=0.01, fill=None, size=0.75) +

    scale_x_datetime(date_labels='%Y', date_breaks='1 year') +
    labs(title='Water Surface Salinity at Sweet Hall Marsh', x='Date', y='Water Surface Salinity (ppt)') +
    theme_bw()
)

print(plot)

plot.save(filename='../../../output/figures/syn_sites_schism_salinity_v2.png',
       height=100, width=190, units='mm', dpi=300)

