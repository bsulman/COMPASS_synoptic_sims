
from plotnine import *
import pandas as pd

# Read
outdf_j = pd.read_csv('../../../output/all_sites_v2_elev_transect.csv')


p = (
        ggplot()

        # 0 line
        + geom_hline(outdf_j, aes(yintercept=0), color="#e6e6e6", size=1.1)

        # Add zone points
        + geom_point(outdf_j.dropna(subset=['zone']),
                     aes(x='dist', y="elev_fromwetland", color="site_id"), size=2)

        # Elevation profile
        + geom_line(outdf_j, aes(x='dist', y="elev_fromwetland", color="site_id"), size=0.9)

        # Zone labels # y="elev_fromwetland+.5",
        + geom_text(outdf_j.dropna(subset=['zone']),
                    aes(x='dist', y=-0.25, label="zone", color="site_id"),
                    size=7, angle=90, va='top')
        # Label each transect
        + geom_text(outdf_j.dropna(subset=['zone']).query('zone=="Upland"'),
                    aes(x='dist+1', y="elev_fromwetland+.1", label="site_id", color="site_id"),
                    size=9, fontweight='5', angle=90, ha='left', va='bottom')
        # Axis labels
        + labs(x="Distance from wetland boundary",
               y='Height(m) above wetland boundary surface')  # y="Orthographic height to NAVD1988")
        # + theme_bw()
        + scale_x_continuous()
        + ylim(-1, 7.5)
        # + scale_y_continuous(limit)
        # + facet_wrap("~site_id", scales="free", ncol=4)
        + theme_bw()
        + theme(legend_position='none',
                panel_grid_major=element_blank(),
                panel_grid_minor=element_blank())
)

# p
p.save(filename='../../../output/figures/syn_sites_v2_elev_transect_rel2wetland_wlabels_v2.png',
       height=140, width=250, units='mm', dpi=300)

