
syn_sites = (pd.read_csv('../surface_data/COMPASS_sites.csv')  # Read file of site locations
             .query('region=="CB"')  # Filter to Chesapeake Bay
             )

# Convert to CRS of DEM
# TODO: are the original coordinates from Ben on WGS84 or NAD83 datum?
syn_sites = (gpd.GeoDataFrame(syn_sites, geometry=gpd.points_from_xy(syn_sites.long, syn_sites.lat, crs="EPSG:4269"))
             .to_crs("EPSG:26918")  # Reproject to DEM's NAD83 / UTM zone 18N
             .rename(columns={"site": "site_id"})
             )

syn_sites['site_cat'] = 'synoptic'
# Reproject sites to DEM
# gdf.to_crs(src.crs.data, inplace=True)

# Save to file
if 0: syn_sites.to_file('../../../data/synoptic_sites/synoptic_sites_pts.geojson')