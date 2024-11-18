import geopandas as gpd
import fiona

# Read KMZ files
gdf1 = gpd.read_file('../../../../data/kmz_from_gdrive/GoodwinIsland.kmz')
gdf2 = gpd.read_file('../../../../data/kmz_from_gdrive/Moneystump Marsh.kmz')
gdf3 = gpd.read_file('../../../../data/kmz_from_gdrive/Sweet Hall Marsh.kmz')
gdf4 = gpd.read_file('../../../../data/kmz_from_gdrive/TEMPEST Plots.kmz')



# Combine into a single GeoDataFrame
combined_gdf = gpd.GeoDataFrame(pd.concat([gdf1, gdf2, gdf3, gdf4], ignore_index=True))

combined_gdf = combined_gdf[combined_gdf.geometry.type == 'Point']

# Export as shapefile
combined_gdf.to_file('../../../output/results/kmz_pts/kmz_pts_cb_combined.shp')