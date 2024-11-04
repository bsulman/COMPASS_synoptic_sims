

# /--------------------------------------------------------------------
#/  Get synoptic groundwater wells data
gw_depth_df = pd.read_csv('../../output/results/sensor_gauges/synoptic_gw_elev.csv')  # synoptic_gw_pressure.csv')
gw_depth_df['TIMESTAMP_hourly'] = pd.to_datetime(gw_depth_df['TIMESTAMP_hourly'], errors='coerce')


#----------------------------------------------------------------------------------
#  Get buoy data

# Read in Buoy data
boundary_wl_df = pd.read_csv(
    '../../output/results/hydro_forcing_gauges/buoy_wl_all_syn_v2.csv',
    low_memory=False)

# Convert datatype
boundary_wl_df['water_salinity'] = pd.to_numeric(boundary_wl_df['water_salinity'], errors='coerce')
boundary_wl_df['water_height_m'] = pd.to_numeric(boundary_wl_df['water_height_m'], errors='coerce')
# boundary_wl_df['total_depth'] = pd.to_numeric(boundary_wl_df['total_depth'], errors='coerce')
boundary_wl_df['datetime'] = pd.to_datetime(boundary_wl_df['datetime'], errors='coerce')


### FILTER TIME
# boundary_wl_df = boundary_wl_df.head(10000)
start_date = '2020-01-01'
end_date = '2023-12-31'

# Filter DataFrame by date range
boundary_wl_df = boundary_wl_df[(boundary_wl_df['datetime'] >= start_date) & (boundary_wl_df['datetime'] <= end_date)]


# ###  TO PLOT GEOM LINES, NEED TO ADD MISSING DATES TO PREVENT LINES OVER GAPS
# df =  gw_depth_df.copy()
# dates = pd.DataFrame()
# # Create a complete range of hourly datetimes from min to max datetime in the DataFrame
# dates['TIMESTAMP_hourly'] = pd.date_range(start=df['TIMESTAMP_hourly'].min(), end=df['TIMESTAMP_hourly'].max(), freq='h')
# gw_depth_df = pd.concat([gw_depth_df, dates], axis=0)

#----------------------------------------------------------------------------------
# from plotnine import ggplot, aes, theme, geom_point, theme_minimal,  labs, geom_histogram, coord_flip, facet_wrap
#/  Plot time series of water depth
from plotnine import *
# import matplotlib as plt
# THIS PREVENTS INTERACTIVE WINDOW ERROR:
# "UserWarning: Starting a Matplotlib GUI outside of the main thread will likely fail."
import matplotlib
matplotlib.use('agg')
from mizani.breaks import date_breaks
from mizani.formatters import date_format
# Prevent continuous warnings from plotnine drawing not working
import warnings
warnings.filterwarnings("ignore")


site_order = ['Crane Creek', 'Portage River','Old Woman Creek',
              'GCReW', 'Goodwin Islands', 'Moneystump Swamp', 'Sweet Hall Marsh']

# Reorder sites for the facets
# erie_hydro_df_3sites['site_name'] = pd.Categorical(erie_hydro_df_3sites['site_name'], categories=site_order, ordered=True)
boundary_wl_df['site_name'] = pd.Categorical(boundary_wl_df['site_name'], categories=site_order, ordered=True)
gw_depth_df['site_name'] = pd.Categorical(gw_depth_df['site_name'], categories=site_order, ordered=True)


# /--------------------------------------------------------------------
#/   PLOT ELEVATION
# p = (
(
    ggplot()

    #Plot Erie buoys water HEIGHT
    # + geom_line(erie_hydro_df_3sites,
    #             aes(x='datetime', y='tide_height_m', color='buoy_name'), size = 0.2)

    # Plot CB buoys water HEIGHT
    + geom_line(boundary_wl_df,
                aes(x='datetime', y='water_height_m', color='zone_name'), size=0.2)

    # Plot in synoptic wells WTD - DEPTH
    + geom_line(gw_depth_df,
               aes(x='TIMESTAMP_hourly', y='gw_elev_m', color='zone_name'), size=0.2)


    + scale_x_datetime(breaks=date_breaks('1 year'), labels=date_format('%Y'))
    + labs(x='', y='Water Elevation (NAVD88, m)')
    + facet_wrap("site_name", scales="free", ncol=3)

    + guides(color=guide_legend(title=""))
    + theme_bw()
    + theme(legend_position= (0.8, 0.1), #'none',
            panel_grid_major=element_blank(),
            panel_grid_minor=element_blank())
            # axis_text_x=element_text(rotation=90, hjust=1))

    ).save('../../output/figures/hydro_forcing_gauges/in_situ_wl_all_ts_v16.png',
       width=12, height=8, dpi=300, verbose = False)




#---------------------------------------------
# Violin plot of water height NAD88 time series plot

ground_elev = gw_depth_df.drop_duplicates(subset=['site_name','zone_name','elev_m'])

erie_hydro_df_3sites['buoy_name'] = 'Hydro boundary'
boundary_wl_df['zone_name'] = 'Hydro boundary'

zone_order = ['Hydro boundary',  'Wetland', 'Transition', 'Upland']
gw_depth_df['zone_name'] = pd.Categorical(gw_depth_df['zone_name'], categories=zone_order, ordered=True)
ground_elev['zone_name'] = pd.Categorical(ground_elev['zone_name'], categories=zone_order, ordered=True)


(
    ggplot()

    #Plot Erie buoys water HEIGHT
    + geom_violin(erie_hydro_df_3sites,
                aes( y='tide_height_m', color='buoy_name', fill='buoy_name'),
                  style='right', size = 0.2)

    # Plot CB buoys water HEIGHT
    + geom_violin(boundary_wl_df,
                aes(x='zone_name', y='tide_height', color='zone_name', fill='zone_name'),
                  style='right', size = 0.2)

    # Plot in synoptic wells WTD - DEPTH
    + geom_violin(gw_depth_df,
               aes(x='zone_name', y='gw_elev_m', color='zone_name', fill='zone_name'),
                  style='right', size = 0.2)

    # Plot ground surface elevation
    + geom_point(ground_elev,
                  aes(x='zone_name', y='elev_m'),
                 shape='_', size=6, color='#000000')

    + labs(x='', y='Water Elevation (NAVD88, m)')
    + facet_wrap("site_name", scales="free", ncol=3)

    + guides(color=guide_legend(title=""))
    + theme_bw()
    + theme(legend_position= (0.8, 0.1), #'none',
            panel_grid_major=element_blank(),
            panel_grid_minor=element_blank())

    ).save('../../output/figures/in_situ_wl_all_ts_15_violin.png',
       width=12, height=8, dpi=300, verbose = False)






# /--------------------------------------------------------------------
#/   PLOT SALINITY                                      ----------

(
    ggplot()

    # Plot CB buoys water HEIGHT
    + geom_line(boundary_wl_df,
                aes(x='datetime', y='water_salinity', color='zone_name'), size=0.2)

    # Plot in synoptic wells WTD - DEPTH
    + geom_line(gw_depth_df,
               aes(x='TIMESTAMP_hourly', y='gw_salinity', color='zone_name'), size=0.2)


    + scale_x_datetime(breaks=date_breaks('1 year'), labels=date_format('%Y'))
    + labs(x='', y='Salinity (PSU)')
    + facet_wrap("site_name", scales="free", ncol=3)

    + guides(color=guide_legend(title=""))
    + theme_bw()
    + theme(legend_position= (0.8, 0.1), #'none',
            panel_grid_major=element_blank(),
            panel_grid_minor=element_blank())
            # axis_text_x=element_text(rotation=90, hjust=1))

    ).save('../../output/figures/hydro_forcing_gauges/in_situ_salinity_v16.png',
       width=12, height=8, dpi=300, verbose = False)





#----------------------------------------------------------------------------------
# Read in buoy forcing data
# boundary_wl_df = pd.read_csv(
#     '../../output/results/hydro_forcing_gauges/buoy_wl_all_syn.csv',
#     low_memory=False)
# tide_heightf.rename(columns=new_column_names)

# # Erie starts in 1987 but data before that is a harmonic fit; Annapolis starts in 1984
# import xarray as xr
# erie_hydro_df= (
#     xr.open_dataset('../data/raw/hydro_forcing/LakeErie_Gageheight_0salt.nc', decode_times=False)
#     .to_dataframe().reset_index()
#     )[843426:-1]  # Subset; because of prev harmonic cycles (approx n=8)
#
#
# start_date = pd.Timestamp('1987-01-01')
# # start_date = pd.Timestamp('1950-01-01')
# # start_time = pd.Timestamp('1987-01-01 00:00:00')
#
# # erie_hydro_df['datetime'] = start_date + pd.to_timedelta(erie_hydro_df['time'], unit='h')
# erie_hydro_df['datetime'] = start_date + pd.to_timedelta(erie_hydro_df['time'] * 15, unit='m')
# # erie_hydro_df['datetime'] = pd.to_datetime(erie_hydro_df['time'], errors='coerce')
# erie_hydro_df
#
# erie_hydro_df_cc = (erie_hydro_df.copy().assign(site_name = 'Crane Creek')) # lambda x: x.gw_depth_m + x.elev)
# erie_hydro_df_owc = (erie_hydro_df.copy().assign(site_name = 'Old Woman Creek'))
# erie_hydro_df_pr = ( erie_hydro_df.copy().assign(site_name = 'Portage River'))
#
#
# erie_hydro_df_3sites = pd.concat([erie_hydro_df_cc, erie_hydro_df_owc, erie_hydro_df_pr], axis=0)
#
#
# # # Filter DataFrame by date range
# # start_date = '2020-01-01'
# # end_date = '2023-12-31'
# # erie_hydro_df_3sites = erie_hydro_df_3sites[(erie_hydro_df_3sites['datetime'] >= start_date) & (erie_hydro_df_3sites['datetime'] <= end_date)]
#
# erie_hydro_df_3sites.info()

# #@@@@@@
# p = (
#     ggplot()
#
#     + geom_hline(gw_depth_df,
#                  yintercept=0, color="#000000", size=0.1)
#
#     # Add zone points
#     + geom_point(gw_depth_df, #[1:2000],
#                  aes(x='TIMESTAMP_hourly', y="gw_depth_m", color="zone_name"), size=0.001)
#
#     # Axis labels
#     + labs(x="Date",
#            y='Hourly water level depth (m) from sensor')  # y="Orthographic height to NAVD1988")
#
#     + coord_trans(y='reverse')
#
#     + scale_x_datetime(breaks=date_breaks('1 year'), labels=date_format('%Y'))
#
#     # change the number of columns
#     + facet_wrap( "site_name", scales="free", ncol=3)
#     )
#
#
# p.save(filename='../../output/figures/gw_depth_plots_nooutlier.png',
#        height=180, width=250, units='mm', dpi=200)

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

#
# #----------------------------------------------------------------------------------
# # Make depth time series plot
#
# # depth_plot = \
# (
#     ggplot(boundary_wl_df) +
#     geom_point(aes(x='datetime', y='total_depth', color='station'), size=0.1) +
#     labs(x='', y='Water depth (m)') +
#     scale_y_reverse()
# ).save('../../output/figures/buoy_depth_timeseries.png',
#        width=8, height=3, dpi=300, verbose = False)
#
#
#
# #----------------------------------------------------------------------------------
# #  PLOT  DISTRIB HEIGHT
# plot = (ggplot(boundary_wl_df, aes(x='tide_height', fill='station'))
#         + geom_histogram(binwidth=0.1, color=None)
#         + coord_flip()
#         + facet_wrap('~station', ncol=2, nrow=2)
#         # + ggtitle("Histogram of Randomly Generated Data")
#         + labs(x="Water height (NAVD, m)", y="Frequency of hourly measurements")
#         + theme(legend_position='none')
#         # + theme_minimal()
#         ).save('../../../output/figures/distrib_tide_height.png',
#                width=4, height=6, dpi=300, verbose = False)
#
# #----------------------------------------------------------------------------------
# #  PLOT  DISTRIB DEPTH
# plot = (ggplot(boundary_wl_df, aes(x='total_depth', fill='station'))
#         + geom_histogram(binwidth=0.1, color=None)
#         + coord_flip()
#         + facet_wrap('~station', ncol=2, nrow=2)
#         # + ggtitle("Histogram of Randomly Generated Data")
#         + labs(x="Water depth (m)",  y="Frequency of hourly measurements")
#         + theme(legend_position='none')
#         # + theme_minimal()
#         ).save('../../../output/figures/distrib_total_depth.png',
#                width=4, height=6, dpi=300, verbose = False)
#
#
# #----------------------------------------------------------------------------------
# # Make salinity plot
# (
#     ggplot(boundary_wl_df, aes(x='datetime', y='tide_height', color='station')) +
#     geom_point(size=0.6) +
#     # theme_bw()
#     labs(x='', y='Water Level (m; NAVD)')  # title='Water depth (m)',
# ).save('../../../output/figures/tide_height_plot.png', width=8, height=6, dpi=300, verbose = False)
#
#
#
#
# # Save plot to file
# # depth_plot.save('../../../output/figures/depth_plot.png', width=8, height=6, dpi=300, verbose = False)
#
#
# #----------------------------------------------------------------------------------
# # Create the point graph using plotnine #
# salinity_plot = (
#     ggplot(df, aes(x='SAMPLE_DATETIME', y='SALINITY')) +
#     geom_point(color='#FF5733') +
#     theme_minimal()
#     # labs(title='Water Level vs Time', x='Time', y='Water Level')
# )
#
# salinity_plot.save('../../../output/figures/goodwin_salinity_plot.pdf', width=6, height=4)
# e('../../../output/figures/goodwin_waterdepth_plot.pdf', width=6, height=4)


