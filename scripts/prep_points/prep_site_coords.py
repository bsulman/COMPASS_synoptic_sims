
import rasterio
from rasterio.merge import merge

# Ohio DEM:  <altdatum>North American Vertical Datum of 1988(GEOID12B)</altdatum>

dem_fps = ['../../data/dem/le/BN19650622.tif',
           '../../data/dem/le/BN19660622.tif']

src_files_to_mosaic = []

for fp in dem_fps:
    src = rasterio.open(fp)
    src_files_to_mosaic.append(src)

# Merge function returns a single mosaic array and the transformation info
mosaic, out_trans = merge(src_files_to_mosaic)


# Update the metadata
out_meta = src.meta.copy()
out_meta.update({"driver": "GTiff",
                 "height": mosaic.shape[1],
                 "width": mosaic.shape[2],
                 "transform": out_trans})
                 # "crs": "+proj=utm +zone=35 +ellps=GRS80 +units=m +no_defs "})


out_fp = '../../data/dem/le/mosaic_BN19650622_BN19650622.tif'
with rasterio.open(out_fp, "w", **out_meta) as dest:
    dest.write(mosaic)


#----------------------------------------------------------------

from prep_points.make_pts_transect import make_pts_transect

# Read in site/zone coordinate file
# Filter to region: Chesapeake Bay
# .query('region=="Chesapeake Bay"')
# Concatenate combinations of sites and land cover in a list of strings
sites = \
    (pd.read_csv('../data/raw/transect_coords/compass_synoptic.csv')
    .assign(grid_points = lambda x: x.site + '_' + x.zone)
    .assign(site_cat = 'synoptic')
    .rename(columns={"site": "site_id"})
     )


# TODO: are the original coordinate datum from Ben in WGS84 or NAD83 ?
sites = \
    (gpd.GeoDataFrame(sites, geometry=gpd.points_from_xy(sites.long, sites.lat, crs="EPSG:4269"))
     # .to_crs("EPSG:26918")  # Reproject to DEM's NAD83 / UTM zone 18N
     .rename(columns={"site": "site_id"})
     )

# Save points to file
if 0:
    sites.to_file('../../data/site_pts/synoptic/synoptic_sites_pts_v2.geojson')


#----------------------------------------------------------------

outdf = pd.DataFrame() # Initialize output df
dem_dir = '../../data/dem/'

# Loop through sites
for site_id in sites.site_id.unique(): #[5:6]:

    print(site_id)

    # Subset df to a single site
    sites_sub = \
        (sites.query('site_id=="' + site_id + '"')
         .reset_index(drop=1)
         )

    # Convert coords to point geometry projected in NAD83
    sites_sub_geom = gpd.points_from_xy(sites_sub.long, sites_sub.lat, crs="EPSG:4269")

    # Reproject depending on which region
    # Convert to projection
    # In Chesapeake: from EPSG 4269 --> 26918 (i.e. NAD83)
    # In Lake Erie:  from EPSG 4269 --> 6549
    # EPSG:26918 NAD83 / UTM zone 18N
    # EPSG:32618 WGS 84 / UTM zone 18N

    # TODO: move this below the transect creation, bc transect making will crash if coords and proj do not match???
    if(sites_sub.region.loc[0] == "Chesapeake Bay"):
        sites_sub = \
            (gpd.GeoDataFrame(sites_sub, geometry=sites_sub_geom)
            .to_crs("EPSG:26918"))  # Reproject to DEM's NAD83 / UTM zone 18N
    else:
        sites_sub = \
            (gpd.GeoDataFrame(sites_sub, geometry=sites_sub_geom)
            .to_crs("EPSG:6549"))

    # Convert to point transect; function returns line and points
    line, pts_transect = make_pts_transect(sites_sub)

    # If no transect is returned, skip to next loop
    if pts_transect is None: continue

    # Save line geometry to file
    # Create dictionary for gdf input
    d = {'col1': ['name1'], 'geometry': [line]}

    # line_gdf = \
    if (sites_sub.region.loc[0] == "Chesapeake Bay"):
        (gpd.GeoDataFrame(d, crs="EPSG:26918")
            .to_file('../../output/results/transect_line/transect_line' + site_id + '.shp'))
    else:
        (gpd.GeoDataFrame(d, crs="EPSG:6549")  # change epsg to 32618?
            .to_file('../../output/results/transect_line/transect_line' + site_id + '.shp'))

    # /-----------------------------------------------------------
    #/  Extract DEM elevation

    # Get DEM tile filename
    dem_filename = dem_dir + sites_sub['dem_tile'].iloc[0]

    # Run zonal stats on transect and elevation from appropriate DEM tile
    from rasterstats import zonal_stats, point_query
    zs = zonal_stats(pts_transect, dem_filename, stats="mean")  # , affine=affine)
    # zs = point_query(pts_transect, dem_filename) # [630]
    zs

    # Write elevation to column
    pts_transect['elev'] = [d['mean'] for d in zs]

    # Spatial join input df and extracted transect, to label transitions points
    out_sub = gpd.sjoin(sites_sub, pts_transect, how='right', predicate='intersects')
    out_sub['site_id'] = sites_sub['site_id'].values[0]

    # Convert GeoDataFrame to regular DataFrame and drop geometry in order to append sites from different projections
    out_sub = pd.DataFrame(out_sub.drop(columns=['index_left','geometry']))

    # Append rows to output dataframe
    outdf = pd.concat([outdf, out_sub], ignore_index=True)




# /-----------------------------------------------------------
#/  Calculate elevation relative to wetland elevation

# Filter to wetland zone only
outdf_filt = \
    (outdf.query('zone=="Wetland"')
    # Select columns
     .loc[:, ['site_id', 'elev','site_cat', 'region']]
     .rename(columns={'elev': 'elev_wetland'})
     )

# Drop columns to be replaced; because we fill every row of these columns in the joining wetland df
outdf = outdf.drop(['site_cat', 'region'], axis=1)

# Rejoin the wetland elevation values to the full transects
outdf_j = (pd.merge(outdf, outdf_filt, on=['site_id'], how='left')
            # Calculate elevation relative to wetland point
           .assign(elev_fromwetland=lambda x: x.elev - x.elev_wetland))



# Save transect elev to CSV file
elev_dir = '../../output/results/elev/'

if 1:
    outdf_j.to_csv(elev_dir + 'synoptic_elev_transect_v3.csv', index=False)

outdf_j = outdf_j.iloc[:,[11,0,10,1,2,3,4,5,6,7,8,9,12]]

(outdf_j.query("zone.notna()", engine='python')
 .drop(columns=['grid_points', 'elev_wetland']) # , 'dem_tile'
 .to_csv(elev_dir + 'synoptic_elev_zone_v3.csv', index=False)
 )

