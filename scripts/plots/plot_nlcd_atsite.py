


# Read in NLCD data
nlcd = (pd.read_csv('../../../data/site_pts/all/nlcd/all_sites_nlcd.csv')
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
                   # cmap="YlGn", cbarlabel="harvest [t/year]")
texts = annotate_heatmap(im, valfmt="{x:.1f} t")

fig.tight_layout()
plt.show()

#----------------------

import numpy as np
from pandas import DataFrame
# index = ['aaa', 'bbb', 'ccc', 'ddd', 'eee']
# columns = ['A', 'B', 'C', 'D']
# df = DataFrame(abs(np.random.randn(5, 4)), index=index, columns=columns)


# fig, ax = plt.subplots()
#
# plt.pcolor(nlcd_wide)
#
# # This uses a custom function in anotehr script
# im, cbar = heatmap(nlcd_wide, nlcd_wide.index, nlcd_wide.columns, ax=ax,
#                    cmap="YlGn", cbarlabel="harvest [t/year]")
# texts = annotate_heatmap(im, valfmt="{x:.1f} t")


# fig.tight_layout()
# plt.show()
# plt.yticks(np.arange(0.5, len(nlcd_wide.index), 1), nlcd_wide.index)
# plt.xticks(np.arange(0.5, len(nlcd_wide.columns), 1), nlcd_wide.columns)


# # Loop over data dimensions and create text annotations.
# for i in range(len(nlcd_wide.index)):
#     for j in range(len(nlcd_wide.columns)):
#         text = ax.text(j, i, nlcd_wide[i, j],
#                        ha="center", va="center", color="w")

# plt.show()
