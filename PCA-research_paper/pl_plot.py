import cds_pca as cds
import matplotlib as mpl
import matplotlib.patches as mpatches

#PL_for_plot_CDXNAIG.xlsx
#PL_for_plot_CDXNAHY.xlsx
print('1. NCCDXIG')
print('2. NCCDXHY')
plot_choice = input('Pick: ')

if plot_choice == '1':
	pl_data = cds.pd.read_excel("../PCA/results/PL_for_plot_CDXNAIG.xlsx", sheetname = 0)

	fig = cds.plt.figure()
	ax1 = fig.add_subplot(1, 1, 1)

	label = pl_data.columns[2:]
	data = cds.np.std(pl_data.iloc[:,2:])/1000000
	threshold = cds.np.std(pl_data.iloc[:,1])/1000000

	index = cds.np.arange(len(label))

	cds.sns.set(style="white", color_codes=True)
	cds.sns.barplot(x=index, y=data, palette = cds.sns.color_palette("Blues"), saturation = .75)
	ax1.set_title('North America H.Y.', pad = 25, fontdict = {'fontsize': 25, 'fontweight' : 'bold'})
	#ax1.ticklabel_format(axis = 'y', style = 'sci', scilimits = (0,0))
	ax1.tick_params(axis = 'y', labelsize = 17)
	#ax1.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
	ax1.set_ylim([0, threshold * 1.3])
	ax1.set_xticks(index, minor=False)
	ax1.set_xticklabels(label, fontdict={'fontsize': 20}, minor=False, rotation=30)
	ax1.set_xlabel('PCA Runs', fontdict = {'fontsize': 20, 'fontweight' : 'bold'})
	ax1.set_ylabel('Standard Deviation (Million)', fontdict = {'fontsize': 20, 'fontweight' : 'bold'})

	ax1.plot([0, 5], [threshold, threshold],  "r", label=pl_data.columns[1], linewidth=4)

	red_patch = mpatches.Patch(color='r', label=pl_data.columns[1] + ' Std Dev')
	cds.plt.legend(handles=[red_patch], loc = 0, fontsize = 15, )

	fig.show()
	fig.savefig('figpath.png', dpi=600, bbox_inches='tight')

elif plot_choice == '2':
	pl_data = cds.pd.read_excel("../PCA/results/PL_for_plot_CDXNAHY.xlsx", sheetname = 0)

	fig = cds.plt.figure()
	ax1 = fig.add_subplot(1, 1, 1)

	label = pl_data.columns[2:]
	data = cds.np.std(pl_data.iloc[:,2:])/1000000
	threshold = cds.np.std(pl_data.iloc[:,1])/1000000

	index = cds.np.arange(len(label))

	cds.sns.set(style="white", color_codes=True)
	cds.sns.barplot(x=index, y=data, palette = cds.sns.color_palette("Blues"), saturation = .75)
	ax1.set_title('North America H.Y.', pad = 25, fontdict = {'fontsize': 25, 'fontweight' : 'bold'})
	#ax1.ticklabel_format(axis = 'y', style = 'sci', scilimits = (0,0))
	ax1.tick_params(axis = 'y', labelsize = 17)
	#ax1.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
	ax1.set_ylim([0, threshold * 1.3])
	ax1.set_xticks(index, minor=False)
	ax1.set_xticklabels(label, fontdict={'fontsize': 20}, minor=False, rotation=30)
	ax1.set_xlabel('PCA Runs', fontdict = {'fontsize': 20, 'fontweight' : 'bold'})
	ax1.set_ylabel('Standard Deviation (Million)', fontdict = {'fontsize': 20, 'fontweight' : 'bold'})

	ax1.plot([0, 4], [threshold, threshold],  "r", label=pl_data.columns[1], linewidth=4)

	red_patch = mpatches.Patch(color='r', label=pl_data.columns[1] + ' Std Dev')
	cds.plt.legend(handles=[red_patch], loc = 0, fontsize = 15, )

	fig.show()
	fig.savefig('figpath.png', dpi=600, bbox_inches='tight')	