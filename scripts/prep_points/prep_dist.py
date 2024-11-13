

def dist_to_nwi_ow(synoptic_pts, nwi):
    # List of strings that you want to filter by
    filter_values = ['Lake', 'Freshwater Pond', 'Riverine', 'Estuarine and Marine Deepwater']
    # Filter the GeoDataFrame where the column values are in the list of strings
    nwi = nwi[nwi['WETLAND_TY'].isin(filter_values)]
    # Reproject
    synoptic_pts_reproj = synoptic_pts.to_crs(nwi.crs)
    # Get distance
    synoptic_pts_reproj['distance'] = synoptic_pts_reproj.geometry.apply(lambda point: nwi.distance(point).min())
    #
    return(synoptic_pts_reproj)



#----------------------
synoptic_pts = gpd.read_file('../../data/site_pts/synoptic/synoptic_sites_pts_v2.geojson')

# Read in NWI
nwi_oh = gpd.read_file('../../data/nwi/OH_Wetlands.shp')
nwi_md = gpd.read_file('../../data/nwi/MD_Wetlands.shp')
nwi_va = gpd.read_file('../../data/nwi/VA_Wetlands.shp')


#----------------------
# Run function calculating distance between points and water
synoptic_pts_dist_oh = dist_to_nwi_ow(synoptic_pts, nwi_oh)
synoptic_pts_dist_md = dist_to_nwi_ow(synoptic_pts, nwi_md)
synoptic_pts_dist_va = dist_to_nwi_ow(synoptic_pts, nwi_va)


#----------------------
#

synoptic_pts_dist_oh = synoptic_pts_dist_oh[synoptic_pts_dist_oh.region=='Lake Erie']
synoptic_pts_dist_md = synoptic_pts_dist_md[synoptic_pts_dist_md.site_id.isin(['Moneystump Swamp','GCReW'])]
synoptic_pts_dist_va = synoptic_pts_dist_va[synoptic_pts_dist_va.site_id.isin(['Sweet Hall Marsh','Goodwin Islands'])]


synoptic_pts_dist_md = synoptic_pts_dist_md.drop(columns='geometry')
synoptic_pts_dist_oh = synoptic_pts_dist_oh.drop(columns='geometry')
synoptic_pts_dist_va = synoptic_pts_dist_va.drop(columns='geometry')


# Concat
synoptic_pts_dist = pd.concat([synoptic_pts_dist_md,
                               synoptic_pts_dist_oh,
                               synoptic_pts_dist_va])#, axis=1)


# Save
synoptic_pts_dist.to_csv('../../data/site_pts/synoptic/synoptic_sites_pts_v2_wdist.csv',
                         index=False)


