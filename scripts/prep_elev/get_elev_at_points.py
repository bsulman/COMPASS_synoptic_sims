
import rasterstats
from rasterstats import zonal_stats
import pandas as pd
import geopandas as gpd


#-----------------------------------------------------------------------------------------------------------------------
# Read site coords with DEM tile IDs

synoptics = \
    (gpd.read_file('../../data/site_pts/synoptic/synoptic_sites_pts_v2.geojson')
     # .query('region=="Chesapeake Bay"')
     .query('site_cat=="synoptic"')
     .query('zone!="water"')
     .query('zone!="sediment"')
    )


# Initialize output df
outdf = pd.DataFrame()

# Loop through sites
for site in synoptics.site_id.unique():

    print(site)

    # Filter df to a single site
    sites_sub = synoptics.query('site_id=="' + site + '"')

    if (sites_sub.region.iloc[0] == "Chesapeake Bay"):
        sites_sub = sites_sub.to_crs("EPSG:26918")
    else:
        sites_sub = sites_sub.to_crs("EPSG:6549")

    # Get DEM tile filename
    dem_filename = '../../data/dem/' + sites_sub['dem_tile'].iloc[0]

    # Extract elevation from correct DEM tile
    zs = zonal_stats(sites_sub, dem_filename, stats="mean")

    print(zs)


#-----------------------------------------------------------------------------------------------------------------------
# Filter to wetland zone only
outdf_filt = (outdf.query('zone=="Wetland"').loc[:, ['site_id', 'site_cat', 'region', 'elev']])
outdf_filt = outdf_filt.rename(columns={'elev': 'elev_wetland'})

# Drop columns to be replaced
outdf = outdf.drop(['site_cat', 'region'], axis=1)

# Rejoin the values to the transects
outdf_j = pd.merge(outdf, outdf_filt, on=['site_id'], how='left')
outdf_j['elev_fromwetland'] = outdf_j['elev'] - outdf_j['elev_wetland']

print(outdf_j.info())


# Save to CSV file
if 1:
    outdf_j.to_csv('../../../output/all_sites_v3_elev_transect.csv', index=False)

