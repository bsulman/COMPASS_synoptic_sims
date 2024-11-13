#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 13:41:07 2024
@author: Etienne Fluet-Chouinard
"""

import pandas as pd
import geopandas as gpd
import geojson

import os
print(os.getcwd())

# Read file of site locations
# sal_stations = (pd.read_csv('../../../data/eotb_salinity/EOTBLongtermStations.csv'))
sal_stations = (pd.read_csv('../../../data/WaterQualityStationStation.csv'))

# Convert coords to point
sal_stations = (gpd.GeoDataFrame(sal_stations, geometry=gpd.points_from_xy(sal_stations.Longitude, sal_stations.Latitude, crs="EPSG:4269"))
        .to_crs("EPSG:26918")
        .reset_index()
        )
sal_stations.info()

# Save points
if 1: sal_stations.to_file('../../../data/waterquality_stations_pts.geojson')


# https://datahub.chesapeakebay.net/API
# GET     WaterQuality/<Start-Date>/<End-Date>/<Data-Stream-Value>/<Program-Id>/<Project-Id>/<Geographical-Attribute>/<Attribute-Id>/<Substance-Id>