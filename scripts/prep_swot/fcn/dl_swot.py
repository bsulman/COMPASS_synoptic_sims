# Water Mask Pixel Cloud NetCDF - SWOT_L2_HR_PIXC_2.0
# Water Mask Pixel Cloud Vector Attribute NetCDF - SWOT_L2_HR_PIXCVec_2.0
# River Vector Shapefile - SWOT_L2_HR_RiverSP_2.0
# Lake Vector Shapefile - SWOT_L2_HR_LakeSP_2.0
# Raster NetCDF - SWOT_L2_HR_Raster_2.0




#--------------------------------------------------------------------------
#  GET LAKE_SP
def dl_lakepoly_persite(x):

    import json
    import earthaccess

    earthaccess.login(strategy='all', persist=True) # 'interactive'
    auth = earthaccess.login()
    # earthaccess.login()

    #  Only need pass and tile, not scene
    # C = Cycle;  P = Pass; T=Tile
    granule_search = '*_' + str(x.swot_pass) + '_' + '*NA*'


    results = (
        earthaccess.search_data(
            short_name = 'SWOT_L2_HR_LakeSP_2.0',
            granule_name = granule_search,
            count = 150,
            temporal = ('2023-01-01 00:00:00', '2024-11-29 23:59:59')))


    #--------------------------------------------------------------------------
    # Save results to json file
    with open('../../data/swot/swot_lakesp_search.json', 'w') as f:
        json.dump(results, f, indent=4)


    # Download last item to folder
    earthaccess.download(results[-10:], "../../data/swot/lakepoly/" + row.site_id + '/')



#--------------------------------------------------------------------------
def dl_pixcvec_persite(row):

    import json
    import earthaccess

    #  Only need pass and tile, not scene
    # C = Cycle;  P = Pass; T=Tile
    granule_search = '*_' + str(row.swot_pass) + '_' + str(row.swot_tile) + str(row.swot_tile_l) + '*'

    results = (
        earthaccess.search_data(
            short_name = 'SWOT_L2_HR_PIXC_2.0',
            granule_name = granule_search,
            count = 150,
            temporal = ('2023-01-01 00:00:00', '2024-11-29 23:59:59')))

    # Get list of granules
    granules = [item["umm"]["GranuleUR"] for item in results]

    # Save search results to file
    with open('../../output/results/swot/swot_pixcvec_search.json', 'w') as f:
        json.dump(results, f, indent=4)

    # DOWNLOAD DATA
    earthaccess.download(results[-10:], "../../data/swot/pixc_vec/" + row.site_id + '/')
