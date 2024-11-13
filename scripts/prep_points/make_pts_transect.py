
# Function creating transect
def make_pts_transect(gdf):

    import numpy as np
    import geopandas as gpd
    from shapely.geometry import MultiPoint  # Point, LineString,
    from shapely.ops import unary_union
    from shapely import LineString, line_locate_point

    # /-----------------------------------------------
    # /  Convert to line
    # gdf = sites_sub

    # Convert points to line
    gdf_geom = gdf['geometry'].tolist()

    # Skip if only a single row
    if int(gdf.shape[0]) == 1: return (None, None)

    # Convert to linestring
    line = LineString(gdf_geom)  # .wkt

    # /-----------------------------------------------
    # / Split line into points at equal intervals, including ends
    distance_delta = 1.0

    # Create array of distance intervals
    distances = np.arange(0, line.length, distance_delta)

    # Interpolate line with points, and append the initial 3 points
    points = [line.interpolate(distance) for distance in distances] + [
        MultiPoint(gdf['geometry'].tolist())]  # [line.boundary]

    multipoint = unary_union(points)  # or new_line = LineString(points)

    # If not a multipoint feature (either bc points too close)
    if multipoint.geom_type != 'MultiPoint':
        return (None, None)

    # Round distance values
    dist = [round(line_locate_point(line, i), 2) for i in multipoint.geoms]

    # Convert to GeoDataFrame
    multipoint = gpd.GeoDataFrame({'dist': dist, 'geometry': multipoint.geoms}, crs=gdf.crs).explode(index_parts=True)

    return (line, multipoint)


#
#
# #----------------------------------------------------------------
# # Reread site coords with tile IDs
#
# import rasterstats
# from rasterstats import zonal_stats
# import pandas as pd
# import geopandas as gpd
#
# # sites = (gpd.read_file('../../../data/site_pts/all/all_sites_pts_v2.geojson')
# sites = (gpd.read_file('../../../data/site_pts/all/all_sites_utm.geojson')
#          .query('region=="Chesapeake Bay"')
#          .query('site_cat=="synoptic"')
#          .query('zone!="water"')
#          .query('zone!="sediment"')
#         )
#
# # Convert to CRS of DEM
# # TODO: are the original coordinates from Ben on WGS84 or NAD83 datum?
# # sites = (gpd.GeoDataFrame(sites, geometry=gpd.points_from_xy(sites.longitude, sites.latitude, crs="EPSG:4269"))
#         # .to_crs("EPSG:26918")  # Reproject to DEM's NAD83 / UTM zone 18N
#         # )
#
#
# outdf = pd.DataFrame() # Initialize output df
#
# # Loop through sites
# for site in sites.site_id.unique():
#     print(site)
#
#     # Filter df to a single site
#     sites_sub = sites.query('site_id=="' + site + '"')
#     # print(sites_sub)
#
#     # Convert to point transect; function returns line and points
#     line, pts_transect = make_pts_transect(sites_sub)
#
#     # If no transect is returned, skip to next loop
#     if pts_transect is None: continue
#
#     # Save line to file
#     d = {'col1': ['name1'], 'geometry': [line]}
#     line_gdf = gpd.GeoDataFrame(d, crs="EPSG:32618")  # (change epsg)
#     line_gdf.to_file('../../../output/results/transect_line/transect_line' + site + '.shp')
#
#     # Get DEM tile filename
#     dem_filename = '../../../data/usgs_dem/' + sites_sub['dem_tile'].iloc[0]
#
#     # Extract elevation from correct DEM tile
#     zs = zonal_stats(pts_transect, dem_filename, stats="mean")  # , affine=affine)
#
#     # write to column
#     pts_transect['elev'] = [d['mean'] for d in zs]
#
#     # spatial join input df and extracted transect, to label transitions points
#     out_sub = gpd.sjoin(sites_sub, pts_transect, how='right', predicate='intersects')
#     out_sub['site_id'] = sites_sub['site_id'].values[0]
#     # print(out_sub)
#
#     # Append rows to output dataframe
#     outdf = pd.concat([outdf, out_sub], ignore_index=True)
#
# # Filter to wetland zone only
# outdf_filt = (outdf.query('zone=="Wetland"').loc[:, ['site_id', 'site_cat', 'region', 'elev']])
# outdf_filt = outdf_filt.rename(columns={'elev': 'elev_wetland'})
#
# # Drop columns to be replaced
# outdf = outdf.drop(['site_cat', 'region'], axis=1)
#
# # Rejoin the values to the transects
# outdf_j = pd.merge(outdf, outdf_filt, on=['site_id'], how='left')
# outdf_j['elev_fromwetland'] = outdf_j['elev'] - outdf_j['elev_wetland']
#
# print(outdf_j.info())
#
#
# # Save to CSV file
# if 1: outdf_j.to_csv('../../../output/all_sites_v2_elev_transect.csv', index=False)
#
