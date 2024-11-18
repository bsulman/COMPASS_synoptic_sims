# -*- coding: utf-8 -*-


# Stations nearby SYNOPTIC sites
# SERC: Annapolis, MD [8575512]
# Goodwin: Yorktown USCG Training Center, VA 8637689
# Moneystump a bit far, further up estuary: Cambridge, MD [8571892]

# /---------------------------------------------------------------#
#/  Get NOAA gauge height data
# from pandas import json_normalize
from py_noaa import coops


df = coops.get_data(
    begin_date="20230101",
    end_date= "20240101",
    stationid="8575512",
    interval='h',
    product="hourly_height", 
    #product= 'salinity',
    bin_num=1,  # Current data and predictions provide information for a specific depth, each depth available for a station has a different Bin number.
    datum='NAVD',
    units="metric",
    time_zone="gmt")  # lst_ldt
    # format='csv')

df.head()


# # /-------------------------------------------------------------
# #/  USGS
#
# # Interactive map:
# # https://dashboard.waterdata.usgs.gov/app/nwd/en/?region=lower48&aoi=default
#
# # https://doi-usgs.github.io/dataRetrieval/articles/Status.html#what-to-expect-dataretrieval-specific
atahub.chesapeakebay.net/WaterQuality