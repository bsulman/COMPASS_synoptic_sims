import numpy as np


# Read in Buoy data
df_wl = pd.read_csv(
    '../../output/results/hydro_forcing_gauges/buoy_wl_all_syn_v4_filled.csv',
    low_memory=False)

#-------------------------------------------------------------------------------
### FILTER TIME AT ALL SITES

# Filter DataFrame by date range
start_date = '2006-01-01';  end_date = '2020-12-31'
df_wl = df_wl[(df_wl['datetime'] >= start_date) & (df_wl['datetime'] <= end_date)]


df_wl = df_wl.sort_values(by=['site_name', 'datetime'])#, ascending=False)


####################################
### CUSTOM FIXES


#-------------------------------------------------------------------------------
# Fill Moneystump WATER LEVEL gap

fill_rows = df_wl[(df_wl.site_name == 'Moneystump Swamp') & (df_wl['datetime'] >=  '2011-01-01') & (df_wl['datetime'] <= '2011-12-31')]
# fill_rows = fill_rows['water_height_m']

# Shift datetime of replacement values by 1 year
gap2013_idx = (df_wl.site_name == 'Moneystump Swamp') & (df_wl['datetime'] >= '2013-01-01') & (df_wl['datetime'] <= '2013-12-31')
gap2014_idx = (df_wl.site_name == 'Moneystump Swamp') & (df_wl['datetime'] >= '2014-01-01') & (df_wl['datetime'] <= '2014-12-31')
gap2015_idx = (df_wl.site_name == 'Moneystump Swamp') & (df_wl['datetime'] >= '2015-01-01') & (df_wl['datetime'] <= '2015-12-31')



## HOLY FUCK - IS THIS REALLY HOW TO UPDATE A COLUMN IN PANDAS
# THIS IS FUCKING RIDICULOUS;  JUST USING iloc modifies a copy
#  THIS SHIT IF RIDICULOUS.  THIS SHIT WOULD BE SO MUCH SIMPLER IN R... WTF IS THIS TRASH
df_wl.iloc[gap2013_idx, df_wl.columns.get_loc('water_height_m')] = fill_rows['water_height_m']
df_wl.iloc[gap2014_idx, df_wl.columns.get_loc('water_height_m')] = fill_rows['water_height_m']
df_wl.iloc[gap2015_idx, df_wl.columns.get_loc('water_height_m')] = fill_rows['water_height_m']

### BTW, YOU CAN'T EVEN REUSE THIS COMMAND TO READ THE CONTENT;
# USE BELOW INSTEAD. WTD!!!!
df_wl.loc[gap2012_idx, 'water_height_m']


#-------------------------------------------------------------------------------
# Fix Sweethall offset
# TODO: VERIFY THAT SHIFT IS NOT BECAUSE OF CHANGE IN DATUM?  DOES VECOS GIVE DATUM OPTION?

df_wl = (df_wl
         .assign(
            water_height_m = lambda x: np.where((df_wl.site_name == 'Sweet Hall Marsh') & (df_wl['datetime'] <= '2016-11-03 12:00:00'),
                                                     x.water_height_m + 0.75,
                                                     x.water_height_m)))


#----------------------------------------------------------------------------------
# Save DataFrame to CSV
df_wl.to_csv('../../output/results/hydro_forcing_gauges/buoy_wl_all_syn_v4_filled_fixed.csv',
                 index=False)

