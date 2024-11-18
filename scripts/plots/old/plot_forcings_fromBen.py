import matplotlib.pyplot as plt

f, a = plt.subplots(num='Water heights', clear=True, nrows=2)
a[0].plot(np.arange(len(grid_points)), surfdata_multicell['ht_above_stream'].squeeze(), ls='-', lw=5.0, color='brown',
          label='Soil surface', drawstyle='steps-mid')
a[0].plot(np.arange(len(grid_points)), tide_data_multicell['tide_height'].mean(dim='time'), color='b', alpha=0.5,
          lw=2.0, label='Mean water level', drawstyle='steps-mid')
# a.axhline(tide_data_multicell['tide_height'].quantile(0.9),color='b',alpha=0.5,ls='--',label='90th percentile water level')
# a.axhline(tide_data_multicell['tide_height'].quantile(0.1),color='b',alpha=0.5,ls='--',label='10th percentile water level')
a[0].fill_between(np.arange(len(grid_points)), tide_data_multicell['tide_height'].quantile(0.1, dim='time'),
                  tide_data_multicell['tide_height'].quantile(0.9, dim='time'), color='b', alpha=0.5,
                  label='Water level', step='mid')

a[0].set_ylabel('Height (m)')
a[0].set(xlim=(0., len(grid_points) - 1.0), title='Site elevations')
# a.legend()

bottom = np.zeros(len(grid_points))
pftnum = 0
for pft in range(surfdata_multicell['PCT_NAT_PFT'].shape[0]):
    if surfdata_multicell['PCT_NAT_PFT'][pft, :].any():
        pftfrac = surfdata_multicell['PCT_NAT_PFT'][pft, :].squeeze()
        a[1].bar(np.arange(len(bottom)), pftfrac, bottom=bottom, color='C%d' % pftnum, label=pftnames[pft],
                 align='center')
        bottom = bottom + pftfrac
        pftnum = pftnum + 1
a[1].legend()
a[1].set(xlim=(0., len(grid_points) - 1.0), title='Site vegetation')
a[1].set_xticks(np.arange(len(grid_points)))
a[1].set_xticklabels(grid_points, rotation=90)
a[0].set_xticks([])

f, a = plt.subplots(num='Water time series', nrows=2, clear=True)
a[0].plot(tide_data_multicell['time'] / (24 * 365), tide_data_multicell['tide_height'][:, 0], c='b')
a[0].axhline(surfdata_multicell['ht_above_stream'].squeeze()[0], ls='--', c='C1', lw=4.0, label='Upland')
a[0].axhline(surfdata_multicell['ht_above_stream'].squeeze()[1], ls='--', c='C2', lw=4.0, label='Transition')
a[0].axhline(surfdata_multicell['ht_above_stream'].squeeze()[2], ls='--', c='C3', lw=4.0, label='Wetland')
a[0].set(title='Chesapeake', xlabel='Time (years)', ylabel='Water level (m)')
a[0].legend()

a[1].plot(tide_data_multicell['time'] / (24 * 365), tide_data_multicell['tide_height'][:, -1], c='b')
a[1].axhline(surfdata_multicell['ht_above_stream'].squeeze()[-3], c='C1', ls='--', lw=4.0)
a[1].axhline(surfdata_multicell['ht_above_stream'].squeeze()[-2], c='C2', ls='--', lw=4.0)
a[1].axhline(surfdata_multicell['ht_above_stream'].squeeze()[-1], c='C3', ls='--', lw=4.0)
a[1].set(title='Lake Erie', xlabel='Time (years)', ylabel='Water level (m)')

plt.show()