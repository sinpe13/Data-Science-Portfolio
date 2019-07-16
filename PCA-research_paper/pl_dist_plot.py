import cds_pca as cds
import matplotlib as mpl
import matplotlib.patches as mpatches
import scipy.stats as stats

pl_data = cds.pd.read_excel("../PCA/results/PL_for_plot_CDXNAIG.xlsx", sheetname = 0)

label = pl_data.columns[1:]
data = pl_data.iloc[:,1:]

fig = cds.plt.figure()



ax1 = fig.add_subplot(3, 1, 1)
cds.sns.set(style="white", color_codes=True)
cds.sns.distplot(data.iloc[:,0], bins=100, kde=False, rug=True, hist_kws={'alpha':.7}, color = 'r')
ax1.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
ax1.set_xlim([-8000000, 8000000])
ax1.set_ylim([0, 10])

ax2 = fig.add_subplot(3, 1, 2)
cds.sns.distplot(data.iloc[:,0], bins=100, kde=False, rug=True, hist_kws={'alpha':.2}, color = 'r')
cds.sns.distplot(data.iloc[:,1], bins=60, kde=False, rug=True, hist_kws={'alpha':1})
ax2.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
ax2.set_xlim([-1500000, 1500000])
ax2.set_ylim([0, 10])

red_patch = mpatches.Patch(color='r', label=pl_data.columns[1], alpha = .2)
cds.plt.legend(handles=[red_patch], loc = 0, fontsize = 10, )

ax3 = fig.add_subplot(3, 1, 3)
cds.sns.distplot(data.iloc[:,0], bins=100, kde=False, rug=True, hist_kws={'alpha':.2}, color = 'r')
cds.sns.distplot(data.iloc[:,2], bins=60, kde=False, rug=True, hist_kws={'alpha':1})
ax3.ticklabel_format(style='sci', axis='x', scilimits=(6,6))
ax3.set_xlim([-3000000, 3000000])
ax3.set_ylim([0, 10])

red_patch = mpatches.Patch(color='r', label=pl_data.columns[1], alpha = .2)
cds.plt.legend(handles=[red_patch], loc = 0, fontsize = 10, )

cds.plt.tight_layout()

fig.show()
fig.savefig('figpath_dist.png', dpi=600, bbox_inches='tight')

##### Second chart ###############

fig = cds.plt.figure()


ax1 = fig.add_subplot(3, 1, 1)
cds.sns.set(style="white", color_codes=True)
cds.sns.distplot(data.iloc[:,0], bins=100, kde=False, rug=True, hist_kws={'alpha':.2}, color = 'r')
cds.sns.distplot(data.iloc[:,3], bins=60, kde=False, rug=True, hist_kws={'alpha':1})
ax1.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
ax1.set_xlim([-6000000, 6000000])
ax1.set_ylim([0, 10])

red_patch = mpatches.Patch(color='r', label=pl_data.columns[1], alpha = .2)
cds.plt.legend(handles=[red_patch], loc = 0, fontsize = 10, )

ax2 = fig.add_subplot(3, 1, 2)
cds.sns.distplot(data.iloc[:,0], bins=100, kde=False, rug=True, hist_kws={'alpha':.2}, color = 'r')
cds.sns.distplot(data.iloc[:,4], bins=60, kde=False, rug=True, hist_kws={'alpha':1})
ax2.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
ax2.set_xlim([-6000000, 6000000])
ax2.set_ylim([0, 10])

red_patch = mpatches.Patch(color='r', label=pl_data.columns[1], alpha = .2)
cds.plt.legend(handles=[red_patch], loc = 0, fontsize = 10, )

#ax2.set_ylim([0, .000005])

ax3 = fig.add_subplot(3, 1, 3)
cds.sns.distplot(data.iloc[:,0], bins=100, kde=False, rug=True, hist_kws={'alpha':.2}, color = 'r')
cds.sns.distplot(data.iloc[:,5], bins=60, kde=False, rug=True, hist_kws={'alpha':1})
ax3.ticklabel_format(style='sci', axis='x', scilimits=(6,6))
ax3.set_xlim([-6000000, 6000000])
ax3.set_ylim([0, 10])

red_patch = mpatches.Patch(color='r', label=pl_data.columns[1], alpha = .2)
cds.plt.legend(handles=[red_patch], loc = 0, fontsize = 10, )

cds.plt.tight_layout()

fig.show()
fig.savefig('figpath_dist_2.png', dpi=600, bbox_inches='tight')

###### Third chart #########################

fig = cds.plt.figure()

ax4 = fig.add_subplot(3, 1, 1)
cds.sns.distplot(data.iloc[:,0], bins=100, kde=False, rug=True, hist_kws={'alpha':.2}, color = 'r')
cds.sns.distplot(data.iloc[:,6], bins=60, kde=False, rug=True, hist_kws={'alpha':1})
ax4.ticklabel_format(style='sci', axis='x', scilimits=(6,6))
ax4.set_xlim([-6000000, 6000000])
ax4.set_ylim([0, 10])

red_patch = mpatches.Patch(color='r', label=pl_data.columns[1], alpha = .2)
cds.plt.legend(handles=[red_patch], loc = 0, fontsize = 10, )


cds.plt.tight_layout()

fig.show()
fig.savefig('figpath_dist_3.png', dpi=600, bbox_inches='tight')