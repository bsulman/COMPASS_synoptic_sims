

# Read in DSWE data
dswe = (pd.read_csv('../../../data/site_pts/all/dswe/all_sites_dswehist.csv')
        .query('site_cat=="synoptic"')
        .drop(['.geo','index','dem_tile','latitude','longitude','site_cat','region'], axis=1))

# Replace system:index
dswe['system:index'] = dswe['system:index'].str.replace('1_', '')
dswe['system:index'] = dswe['system:index'].str.replace('2_', '')
dswe['system:index'] = dswe['system:index'].str.replace('LC08_', '')
dswe['system:index'] = dswe['system:index'].str.replace('LE07_', '')
dswe['system:index'] = dswe['system:index'].str.replace('014033_', '')
dswe['system:index'] = dswe['system:index'].str.replace('014034_', '')
dswe['system:index'] = dswe['system:index'].str.replace('015034_', '')
dswe['system:index'] = dswe['system:index'].str.replace('015033_', '')

# Get first 6 digits
dswe['system:index'] = [x[:6] for x in dswe['system:index']]

# Add day 01
dswe['system:index'] = dswe['system:index'] + '01'

# Convert to date
dswe['datetime'] = pd.to_datetime(dswe['system:index'], format='mixed') #'%Y%m%d')

# Head
dswe['datetime'].head(100)





#---------------------------------------------------------------------------------------
from plotnine import ggplot, aes, geom_point, scale_x_datetime, labs, theme_bw

import matplotlib
matplotlib.use('agg')


plot = (
    ggplot() +
    geom_point(dswe, aes(x='datetime', y='wetcount', color='site_id', shape='site_id'), stroke=0.01, fill=None, size=0.75) +
    # geom_point(df_sweethall, aes(x='SAMPLE_DATETIME', y='SALINITY', color='data_source', shape='data_source'), stroke=0.01, fill=None, size=0.75) +
    # geom_point(df_goodwin, aes(x='SAMPLE_DATETIME', y='SALINITY', color='STATION', shape='data_source'), stroke=0.01, fill=None, size=0.75) +

    scale_x_datetime(date_labels='%Y', date_breaks='1 year') +
    # labs(title='Water Surface Salinity at Sweet Hall Marsh', x='Date', y='Water Surface Salinity (ppt)') +
    theme_bw()
).save('../../../output/figures/heatmap_dswe.png',
               width=4, height=3, dpi=300, verbose = False)

# plot.show()
# print(plot)

# plot.save(filename='../../../output/figures/syn_sites_schism_salinity_v2.png',
#        height=100, width=190, units='mm', dpi=300)


(ggplot() +
    geom_point(dswe, aes(x='datetime', y='wetcount', color='site_id', shape='site_id'), stroke=0.01, fill=None, size=0.75))