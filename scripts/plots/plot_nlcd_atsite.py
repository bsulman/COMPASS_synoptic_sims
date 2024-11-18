


# Read in NLCD data
nlcd = \
        (pd.read_csv('../../../data/site_pts/all/nlcd/all_sites_nlcd.csv')
        .query('site_cat=="synoptic"')
        .drop(['system:index', '.geo','index','dem_tile','latitude','longitude','site_cat','region'], axis=1))

# Pivot to wide;  as a matrix shape
nlcd_wide = nlcd.pivot(index = 'site_id', columns = 'zone', values = 'landcover').reset_index().set_index('site_id')#

# Reorder columns
nlcd_wide = nlcd_wide[['Wetland','Transition','Upland']]

#### This reordering did not work
# nlcd_wide.columns = pd.Categorical(nlcd_wide.columns, categories=['Wetland','Transition','Upland'])
# nlcd_wide.columns.reorder_categories(['Wetland','Transition','Upland'], ordered=True)


#------------------------------------------
# Generage plot

import matplotlib.pyplot as plt

fig, ax = plt.subplots()
im, cbar = heatmap(nlcd_wide, nlcd_wide.index, nlcd_wide.columns, ax=ax)
texts = annotate_heatmap(im, valfmt="{x:.1f} t")

fig.tight_layout()
plt.show()
