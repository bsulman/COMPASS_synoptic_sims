
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



