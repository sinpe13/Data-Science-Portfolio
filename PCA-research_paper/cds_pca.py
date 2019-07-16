import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import norm
from sklearn.preprocessing import StandardScaler
from scipy import stats
from sklearn.decomposition import PCA
import warnings
import datetime
warnings.filterwarnings('ignore')

class CDS():

	def __init__(self):
		self.df = pd.DataFrame()

	def connect_db(self,sql_cds = """SELECT [Date],[Mnemonic] as Ticker,[RedCode],[Tier],[Ccy],[DocClause],[Contributor],[Spread5y],[Recovery],[CompositeCurveRating],[Sector],[Region],[Country],[AvRating],[ImpliedRating] FROM [hobbit].[dbo].[CDS] AND [Tier] = 'SNRFOR'"""):

		con = pyodbc.connect('Trusted_Connection=yes', driver = '{ODBC Driver 11 for SQL Server}',server = 'PETERSINKA\PETERSINKA', database = 'hobbit')
		sql = sql_cds
		self.df = pd.read_sql(sql, con)


	def cds_data_transform(self, cut_threshold = 2000):

		df = self.df

		base_df = df[['Date','Ticker','Spread5y']].drop_duplicates(['Date','Ticker'], keep='last').set_index(['Date', 'Ticker'])


		df_work= base_df.unstack(-1)
		df_work.columns = df_work.columns.droplevel()

		#Pick tickers with enough data (at least 90% filled)
		tickers = []
		for i in range(len(df_work.columns)):
			if df_work.iloc[:,i].count() > cut_threshold:
				tickers.append(df_work.columns[i])

		# forward fill and then backfill 
		df_clean = df_work[tickers]
		df_clean.fillna(method='ffill', inplace = True)
		df_clean.fillna(method='bfill', inplace = True)	

		#calculating log return
		df_clean = (np.log(df_clean) - np.log(df_clean.shift(1))).iloc[1:,:]

		self.df = df_clean

def plot_variance(eigen_vals):

	##### Plot eigenvalues
	tot = sum(eigen_vals)
	var_exp = [(i / tot) for i in sorted(eigen_vals, reverse=True)]
	cum_var_exp = np.cumsum(var_exp)

	plt.bar(range(len(eigen_vals)), var_exp[:len(eigen_vals)], alpha=0.5, align='center',label='individual explained variance')
	plt.step(range(len(eigen_vals)), cum_var_exp[:len(eigen_vals)], where='mid',label='cumulative explained variance')
	plt.ylabel('Explained variance ratio')
	plt.xlabel('Principal components')
	plt.legend(loc='best')
	plt.show()

	####### DATA EXPLORATION ###############
def desc_stat(df_clean,df_cdx):
	print('Description statistics')
	df_cdx.describe()
	print('Histogram of the data')
	sns.distplot(df_cdx)
	
	#skewness and kurtosis
	print("Skewness: %f" % df_cdx.skew())
	print("Kurtosis: %f" % df_cdx.kurt())

	#correlation matrix
	corrmat = df_clean.corr()
	f, ax = plt.subplots(figsize=(12, 9))
	sns.heatmap(corrmat, vmax=.8, square=True);

	#outliers
	print('Investigate outliers')
	scaled_data = StandardScaler().fit_transform(df_cdx[:,np.newaxis]);
	low_range = scaled_data[scaled_data[:,0].argsort()][:10]
	high_range= scaled_data[scaled_data[:,0].argsort()][-10:]
	print('outer range (low) of the distribution:')
	print(low_range)
	print('\nouter range (high) of the distribution:')
	print(high_range)

	#histogram and normal probability plot
	sns.distplot(df_cdx, fit=norm);
	fig = plt.figure()
	res = stats.probplot(df_cdx, plot=plt)

	##applying log transformation
	#log_df_cdg = np.log(df_cdx)
	##transformed histogram and normal probability plot
	#sns.distplot(log_df_cdg, fit=norm);
	#fig = plt.figure()
	#res = stats.probplot(log_df_cdg, plot=plt)

	plt.show()

def generate_eff_front(df_clean,pca_result,df_cdx):

	#set number of runs of random portfolio weights
	num_portfolios = 25000
	num_cds_from_pca = pca_result.shape[1]
	number_of_all_cds = df_clean.shape[1]

    #select  weights for portfolio holdings
	weights = (np.ones(num_cds_from_pca) / num_cds_from_pca)

    #set up array to hold results
	results = np.zeros((3,num_portfolios))
	 
	 
	for i in range(num_portfolios):
	 
		portfolio_index = np.random.choice(number_of_all_cds, num_cds_from_pca, replace=False)

		returns = df_clean.iloc[:,portfolio_index]

		#calculate mean daily return and covariance of daily returns
		mean_daily_returns = returns.mean()
		cov_matrix = returns.cov()

	    #calculate portfolio return and volatility
		portfolio_return = np.sum(mean_daily_returns * weights)# * 252
		portfolio_std_dev = np.sqrt(np.dot(weights.T,np.dot(cov_matrix, weights))) #* np.sqrt(252)
	 
	    #store results in results array
		results[0,i] = portfolio_return
		results[1,i] = portfolio_std_dev
	    #store Sharpe Ratio (return / volatility) - risk free rate element excluded for simplicity
		results[2,i] = results[0,i] / results[1,i]
	 
	#convert results array to Pandas DataFrame
	results_frame = pd.DataFrame(results.T,columns=['ret','stdev','sharpe'])
	 
	#create scatter plot coloured by Sharpe Ratio
	plt.scatter(results_frame.stdev,results_frame.ret,c=results_frame.sharpe,cmap='RdYlBu')
	plt.colorbar()

	# Add PCA portfolio to the plot
	returns = pca_result

	#calculate mean daily return and covariance of daily returns
	mean_daily_returns = returns.mean()
	cov_matrix = returns.cov()
	   #calculate portfolio return and volatility
	portfolio_return = np.sum(mean_daily_returns * weights) #* 252
	portfolio_std_dev = np.sqrt(np.dot(weights.T,np.dot(cov_matrix, weights))) #* np.sqrt(252)

	#plot red star to highlight position of the PCA portfolio 
	plt.scatter(portfolio_std_dev,portfolio_return,marker=(5,1,0),color='r',s=1000)

	# Add PCA portfolio to the plot
	returns = df_cdx

	#calculate mean daily return and covariance of daily returns
	mean_daily_returns = returns.mean()
	portfolio_std_dev = returns.std()
	#calculate portfolio return and volatility
	portfolio_return = np.sum(mean_daily_returns) #* 252
	#portfolio_std_dev = np.sqrt(np.dot(weights.T,np.dot(cov_matrix, weights))) * np.sqrt(252)

	#plot green star to highlight position of CDS index
	plt.scatter(portfolio_std_dev,portfolio_return,marker=(5,1,0),color='g',s=1000)

	plt.show()

def main_menu():

	print('Choose which data to input for CDS data: ')	
	print('1. All CDS: ')
	print('2. NA CDS: ')
	print('3. NA and EU CDS: ')
	print('4. NA CDS (2006 - 2009): ')
	print('5. EU CDS (2006 - 2009): ')
	print('6. NA CDS (2004-2006): ')
	print('7. EU CDS (2004-2006): ')
	print('8. NA CDS (2010-2014): ')
	print('9. EU CDS (2010-2014): ')
	print('10. Asia ex Japan CDS (2006 - 2009): ')
	print('11. NA CDS IG (2010-2011) most liquid: ')
	print('12. NA CDS HY (2010-2011) most liquid: ')
	print('13. EU CDS IG (2010-2011) most liquid: ')
	print('14. EU CDS HY (2010-2011) most liquid: ')
	print('15. NA CDS IG (2017-2018) most liquid: ')
	print('16. NA CDS HY (2017-2018) most liquid: ')
	print('17. EU CDS IG (2017-2018) most liquid: ')
	print('18. EU CDS HY (2017-2018) most liquid: ')
	print('0.: Exit')

	while True:
		    cds_input = input('Enter your choice: ')
		    try:
		       cds_input = int(cds_input)
		    except ValueError:
		       print ('Valid number, please')
		       continue
		    if 0 <= cds_input <= 18:
		       break
		    else:
		       print ('Valid range, please ')


	if cds_input == 1:
		cds_individual_portfolio = CDS()
		cds_individual_portfolio.connect_db()
		cds_individual_portfolio.cds_data_transform()
		df_clean = cds_individual_portfolio.df


	elif cds_input == 2:
		sql_CDS = """SELECT [Date],,[Mnemonic] as Ticker,[RedCode],[Tier],[Ccy],[DocClause],[Contributor],[Spread5y],[Recovery],[CompositeCurveRating],[Sector],[Region],[Country],[AvRating],[ImpliedRating] FROM [hobbit].[dbo].[CDS]
				WHERE [Region]='N.Amer' AND [Tier] = 'SNRFOR'"""

		cds_individual_portfolio = CDS()
		cds_individual_portfolio.connect_db(sql_CDS)
		cds_individual_portfolio.cds_data_transform()	
		df_clean = cds_individual_portfolio.df

	elif cds_input == 3:
		sql_CDS = """SELECT [Date],[Mnemonic] as Ticker,[RedCode],[Tier],[Ccy],[DocClause],[Contributor],[Spread5y],[Recovery],[CompositeCurveRating],[Sector],[Region],[Country],[AvRating],[ImpliedRating] FROM [hobbit].[dbo].[CDS]
				WHERE [Region] IN ('N.Amer', 'Europe') AND [Tier] = 'SNRFOR'"""

		cds_individual_portfolio = CDS()
		cds_individual_portfolio.connect_db(sql_CDS)
		cds_individual_portfolio.cds_data_transform()	
		df_clean = cds_individual_portfolio.df

	elif cds_input == 4:
		sql_CDS = """SELECT [Date],[Mnemonic] as Ticker,[RedCode],[Tier],[Ccy],[DocClause],[Contributor],[Spread5y],[Recovery],[CompositeCurveRating],[Sector],[Region],[Country],[AvRating],[ImpliedRating] FROM [hobbit].[dbo].[CDS]
				WHERE [Region] = 'N.Amer' AND [Tier] = 'SNRFOR'  AND (Date >= '01/01/2006') AND (Date < '01/01/2010')"""

		cds_individual_portfolio = CDS()
		cds_individual_portfolio.connect_db(sql_CDS)
		cds_individual_portfolio.cds_data_transform(600)	
		df_clean = cds_individual_portfolio.df

	elif cds_input == 5:
		sql_CDS = """SELECT [Date],[Mnemonic] as Ticker,[RedCode],[Tier],[Ccy],[DocClause],[Contributor],[Spread5y],[Recovery],[CompositeCurveRating],[Sector],[Region],[Country],[AvRating],[ImpliedRating] FROM [hobbit].[dbo].[CDS]
				WHERE [Region] = 'Europe' AND [Tier] = 'SNRFOR'  AND (Date >= '01/01/2006') AND (Date < '01/01/2010')"""

		cds_individual_portfolio = CDS()
		cds_individual_portfolio.connect_db(sql_CDS)
		cds_individual_portfolio.cds_data_transform(600)	
		df_clean = cds_individual_portfolio.df

	elif cds_input == 6:
		sql_CDS = """SELECT [Date],[Mnemonic] as Ticker,[RedCode],[Tier],[Ccy],[DocClause],[Contributor],[Spread5y],[Recovery],[CompositeCurveRating],[Sector],[Region],[Country],[AvRating],[ImpliedRating] FROM [hobbit].[dbo].[CDS]
				WHERE [Region] = 'N.Amer' AND [Tier] = 'SNRFOR'  AND (Date < '01/01/2006') AND (Date >= '09/20/2004')"""

		cds_individual_portfolio = CDS()
		cds_individual_portfolio.connect_db(sql_CDS)
		cds_individual_portfolio.cds_data_transform(200)	
		df_clean = cds_individual_portfolio.df

	elif cds_input == 7:
		sql_CDS = """SELECT [Date],[Mnemonic] as Ticker,[RedCode],[Tier],[Ccy],[DocClause],[Contributor],[Spread5y],[Recovery],[CompositeCurveRating],[Sector],[Region],[Country],[AvRating],[ImpliedRating] FROM [hobbit].[dbo].[CDS]
				WHERE [Region] = 'Europe' AND [Tier] = 'SNRFOR'  AND (Date < '01/01/2006') AND (Date >= '09/20/2004')"""

		cds_individual_portfolio = CDS()
		cds_individual_portfolio.connect_db(sql_CDS)
		cds_individual_portfolio.cds_data_transform(200)	
		df_clean = cds_individual_portfolio.df

	elif cds_input == 8:
		sql_CDS = """SELECT [Date],[Mnemonic] as Ticker,[RedCode],[Tier],[Ccy],[DocClause],[Contributor],[Spread5y],[Recovery],[CompositeCurveRating],[Sector],[Region],[Country],[AvRating],[ImpliedRating] FROM [hobbit].[dbo].[CDS]
				WHERE [Region] = 'N.Amer' AND [Tier] = 'SNRFOR'  AND (Date < '09/20/2014') AND (Date >= '01/01/2010')"""

		cds_individual_portfolio = CDS()
		cds_individual_portfolio.connect_db(sql_CDS)
		cds_individual_portfolio.cds_data_transform(900)	
		df_clean = cds_individual_portfolio.df

	elif cds_input == 9:
		sql_CDS = """SELECT [Date],[Mnemonic] as Ticker,[RedCode],[Tier],[Ccy],[DocClause],[Contributor],[Spread5y],[Recovery],[CompositeCurveRating],[Sector],[Region],[Country],[AvRating],[ImpliedRating] FROM [hobbit].[dbo].[CDS]
				WHERE [Region] = 'Europe' AND [Tier] = 'SNRFOR'  AND (Date < '09/20/2014') AND (Date >= '01/01/2010')"""

		cds_individual_portfolio = CDS()
		cds_individual_portfolio.connect_db(sql_CDS)
		cds_individual_portfolio.cds_data_transform(900)	
		df_clean = cds_individual_portfolio.df

	elif cds_input == 10:
		sql_CDS = """SELECT [Date],[Mnemonic] as Ticker,[RedCode],[Tier],[Ccy],[DocClause],[Contributor],[Spread5y],[Recovery],[CompositeCurveRating],[Sector],[Region],[Country],[AvRating],[ImpliedRating] FROM [hobbit].[dbo].[CDS]
				WHERE [Region] in ('Asia', 'India') AND [Country] != 'Japan' AND [Tier] = 'SNRFOR'  AND (Date >= '01/01/2006') AND (Date < '01/01/2010')"""

		cds_individual_portfolio = CDS()
		cds_individual_portfolio.connect_db(sql_CDS)
		cds_individual_portfolio.cds_data_transform(600)	
		df_clean = cds_individual_portfolio.df

	elif cds_input == 11:
		sql_CDS = """SELECT [Date],[Mnemonic] as Ticker,[RedCode],[Tier],[Ccy],[DocClause],[Contributor],[Spread5y],[Recovery],[CompositeCurveRating],[Sector],[Region],[Country],[AvRating],[ImpliedRating] FROM [hobbit].[dbo].[CDS]
				WHERE [Tier] = 'SNRFOR'  AND (Date < '03/21/2011') AND (Date >= '09/20/2010') AND [Mnemonic] in 
					('Covidien Ltd',
						'Freeport McMoRan Corp',
						'Rio Tinto Alcan Inc',
						'Spectra Energy Cap LLC',
						'Time Warner Entmt Co LP',
						'Unum Group',
						'Burlington Northern Santa Fe LLC',
						'Cameron Intl Corp',
						'Cap One Bk USA Natl Assn',
						'Developers Diversified Rlty Corp',
						'EOP Oper Ltd Pship',
						'HCP, Inc.',
						'Maytag Corp',
						'Merck Sharp & Dohme Corp',
						'Noble Corp',
						'NY City NY',
						'Pepsico Inc',
						'Philip Morris Intl Inc',
						'St of NJ',
						'St of NY',
						'Stanley Black & Decker Inc',
						--'Sun Microsystems Inc',
						'Thomson Reuters Corp',
						'Trane Inc.',
						'Travelers Cos Inc',
						'Triad Healthcare Corp',
						'UST LLC',
						'Westn Un Co',
						'WYETH LLC',
						'XTO Engy Inc',
						'CenturyLink Inc',
						'Enterprise Prods Oper LLC',
						'ERAC USA Fin LLC',
						'HP Enterprise Services LLC',
						'Interval Acquisition Corp',
						'Manor Care Inc',
						'Motorola Inc',
						'Oracle America Inc',
						'Oracle Corp',
						--'Southern Co Cap Fdg Inc',
						'Teck Res Ltd',
						'The Gap Inc',
						'TIME WARNER CABLE INC',
						'TX Instrs Inc',
						'Tyson Foods Inc',
						'Weatherford Intl Inc',
						'XL Group Ltd',
						'Xstrata Canada Corp',
						'1st Data Corp',
						'3M Co',
						'Abbott Labs',
						'ACE Ltd',
						'Aetna Inc.',
						'Agrium Inc',
						'Air Prods & Chems Inc',
						'Alcoa Inc.',
						'Allegheny Engy Supp Co LLC',
						'Allergan Inc',
						'Allied Waste North Amer Inc',
						'Allstate Corp',
						'Altria Gp Inc',
						'AmerisourceBergen Corp',
						'Amern Elec Pwr Co Inc',
						'Amern Express Co',
						'Amern Intl Gp Inc',
						'Amgen Inc.',
						'Anadarko Pete Corp',
						'Anheuser Busch Cos Inc',
						'Aon Corp',
						'Apache Corp',
						'Archer Daniels Midland Co',
						'Arrow Electrs Inc',
						'Assur Gty Corp',
						'AT&T Corp.',
						'AT&T Inc',
						'AT&T Mobility LLC',
						'Autozone Inc',
						'Avalon Bay Cmntys Inc',
						'Avnet, Inc.',
						'Avon Prods Inc',
						'Baker Hughes Inc',
						'Barrick Gold Corp',
						'Baxter Intl Inc',
						'BCE Inc',
						'BellSouth Corp',
						'Berkshire Hathaway Inc',
						'Best Buy Co Inc',
						'Bk of America Corp',
						'Black & Decker Corp',
						'Boeing Cap Corp',
						'Boeing Co',
						'BorgWarner Inc',
						'Boston Pptys Ltd Partnership',
						'Boston Scientific Corp',
						'Bristol Myers Squibb Co',
						'Bunge Ltd Fin Corp',
						'CA, Inc.',
						'Campbell Soup Co',
						'Cap One Finl Corp',
						'Cardinal Health Inc',
						'Cargill Inc',
						'Carnival Corp',
						'Caterpillar Finl Svcs Corp',
						'Caterpillar Inc',
						'CBS Corp',
						'Cdn Nat Res Ltd',
						'Cdn Natl Rwy Co',
						'Centerpoint Engy Inc',
						'Centerpoint Engy Res Corp',
						'Centex Corp',
						'Chevron Corp',
						'Chubb Corp',
						'Cigna Corp',
						'Cisco Sys Inc',
						'Citigroup Inc',
						'Clorox Co',
						'CMS Engy Corp',
						'CNA Finl Corp',
						'Coca Cola Co',
						--'Coca Cola Entpers Inc',
						'Colgate Palmolive Co',
						'Comcast Cable Comms LLC',
						'Comcast Corp',
						'Coml Metals Co',
						'Computer Sciences Corp',
						'Con way Inc',
						'ConAgra Foods Inc',
						'ConocoPhillips',
						'Consol Edison Co NY Inc',
						'Constellation Engy Gp Inc',
						'Corning Inc',
						'Costco Whsl Corp',
						'Cox Comms Inc',
						'Cr Suisse USA Inc',
						'CSX Corp',
						'Cummins Inc',
						'CVS Caremark Corp',
						'Cytec Inds Inc',
						'D T E Engy Co',
						'Danaher Corp',
						'Darden Restaurants Inc',
						'Deere & Co',
						'Delhaize Gp',
						'Dell Inc',
						'Devon Engy Corp',
						'Diamond Offshore Drilling Inc',
						'DIRECTV Hldgs LLC',
						'Dominion Res Inc',
						'Dover Corp',
						'Dow Chem Co',
						'DPL Inc',
						'DUKE Rlty Ltd PARTNERSHIP',
						'E I du Pont de Nemours & Co',
						'Eastman Chem Co',
						'Eaton Corp',
						'Eli Lilly & Co',
						'Embarq Corp',
						'Emerson Elec Co',
						'Enbridge Engy Partners LP',
						'Enbridge Inc',
						'EnCana Corp',
						'Energy Transfer Partners LP',
						'ENSCO Intl Inc',
						'EOG Res Inc',
						'ERP Oper Ltd Pship',
						'Exelon Corp',
						'Exelon Generation Co LLC',
						'EXPEDIA INC',
						'Exxon Mobil Corp',
						'Fairfax Finl Hldgs Ltd',
						'FedEx Corp',
						'FirstEnergy Corp',
						'Fortune Brands Inc',
						'Freeport McMoran Copper & Gold Inc',
						'G A T X Corp',
						'Gen Dynamics Corp',
						'Gen Elec Cap Corp',
						'Gen Mls Inc',
						'Genworth Finl Inc',
						'Goldman Sachs Gp Inc',
						'Goodrich Corp',
						'H J Heinz Co',
						'Halliburton Co',
						--'Hartford Finl Svcs Gp Inc',
						'Hasbro Inc',
						'Health Care REIT Inc',
						'Hershey Co',
						'Hess Corp',
						'Hewlett Packard Co',
						'Home Depot Inc',
						'Honeywell Intl Inc',
						'HSBC Fin Corp',
						'Humana Inc',
						'Husky Engy Inc',
						'IL Tool Wks Inc',
						'Ingersoll Rand Co Ltd',
						'Intl Business Machs Corp',
						'Intl Game Tech',
						'Intl Lease Fin Corp',
						'Intl Paper Co',
						'John Deere Cap Corp',
						'Johnson & Johnson',
						'Johnson Ctls Inc',
						'JPMorgan Chase & Co',
						'Kellogg Co',
						'Kerr Mcgee Corp',
						'KeySpan Corp',
						'Kimberly Clark Corp',
						'Kimco Rlty Corp',
						'Kinder Morgan Engy Partners L P',
						'Kohls Corp',
						'Kraft Foods Inc',
						'L 3 Comms Corp',
						'Lexmark Intl Inc',
						'Liberty Mut Ins Co',
						'Lincoln Natl Corp',
						'Lockheed Martin Corp',
						'Loews Corp',
						'Lowes Cos Inc',
						'Lubrizol Corp',
						'M D C Hldgs Inc',
						'Marathon Oil Corp',
						'Marriott Intl Inc',
						'Marsh & Mclennan Cos Inc',
						'Martin Marietta Matls Inc',
						'Masco Corp',
						'Mattel Inc',
						'McDonalds Corp',
						'McKesson Corp',
						'MeadWestvaco Corp',
						'MEDCO HEALTH SOLUTIONS INC',
						'Medtronic Inc',
						'Merck & Co Inc',
						'Merrill Lynch & Co Inc',
						'MetLife Inc',
						'Monsanto Co',
						'Morgan Stanley',
						'Murphy Oil Corp',
						'Nabors Inds Inc',
						'Natl Rural Utils Coop Fin Corp',
						'New Cingular Wireless Services Inc',
						'Newell Rubbermaid Inc',
						'Newmont Mng Corp',
						'Newmont USA Ltd',
						'News America Inc',
						'Nexen Inc',
						'NiSource Fin Corp',
						'Noble Engy Inc',
						'Nordstrom Inc',
						'Norfolk Sthn Corp',
						'Northrop Grumman Corp',
						'Nucor Corp',
						'Occidental Pete Corp',
						'Odyssey Re Hldgs Corp',
						'Omnicom Gp Inc',
						'Oneok Inc',
						'Pac Gas & Elec Co',
						'Packaging Corp Amer',
						'Pactiv Corp',
						'Pepco Hldgs Inc',
						'Pfizer Inc',
						'Pitney Bowes Inc',
						'Potash Corp Sask Inc',
						'PPG Inds Inc',
						'PPL Engy Supp LLC',
						'Praxair Inc',
						'Pride Intl Inc',
						'Procter & Gamble Co',
						'Progress Engy Inc',
						'ProLogis',
						'Prudential Finl Inc',
						'PSEG Pwr LLC',
						'Quest Diagnostics Inc',
						'R R Donnelley & Sons Co',
						'Raytheon Co',
						'Rep Svcs Inc',
						'Reynolds Amern Inc',
						'Rohm & Haas Co',
						'RPM Intl Inc',
						'Ryder Sys Inc',
						'Safeway Inc',
						'Sara Lee Corp',
						'Schlumberger NV',
						'Sempra Engy',
						'Shaw Comms Inc',
						'Sherwin Williams Co',
						'Simon Ppty Gp L P',
						'SLM Corp',
						'Southwest Airls Co',
						'Staples Inc',
						'Sthn CA Edison Co',
						'Suncor Engy Inc',
						'Sunoco Inc',
						'Talisman Engy Inc',
						'Target Corp',
						'TECO Engy Inc',
						'Telus Corp',
						'Temple Inland Inc',
						'The Kroger Co.',
						'Time Warner Inc',
						'TJX Cos Inc',
						'Toll Bros Inc',
						'Torchmark Corp',
						'TransCanada Pipelines Ltd',
						'U S Bancorp',
						'Un Pac Corp',
						'UnitedHealth Gp Inc',
						'Unvl Corp',
						'Utd Parcel Svc Inc',
						'Utd Sts Cellular Corp',
						'Utd Tech Corp',
						'V F Corp',
						'Verizon Comms Inc',
						'Viacom',
						'Vornado Rlty LP',
						'Vulcan Matls Co',
						'Wal Mart Stores Inc',
						'Walt Disney Co',
						'Waste Mgmt Inc',
						'Weatherford Intl Ltd',
						'WellPoint Inc',
						'Wells Fargo & Co',
						'Weyerhaeuser Co',
						'Whirlpool Corp',
						'Williams Cos Inc',
						'Xcel Engy Inc',
						'Xerox Corp',
						--'XL Cap Ltd',
						'YUM Brands Inc',
						'Duke Energy Carolinas LLC',
						'Transocean Inc',
						'Valero Energy Corp',
						'TYCO Electrs LTD',
						'Tyco Intl Ltd'	
						)"""

		cds_individual_portfolio = CDS()
		cds_individual_portfolio.connect_db(sql_CDS)
		cds_individual_portfolio.cds_data_transform(100)	
		df_clean = cds_individual_portfolio.df

	elif cds_input == 12:
		sql_CDS = """SELECT [Date],[Mnemonic] as Ticker,[RedCode],[Tier],[Ccy],[DocClause],[Contributor],[Spread5y],[Recovery],[CompositeCurveRating],[Sector],[Region],[Country],[AvRating],[ImpliedRating] FROM [hobbit].[dbo].[CDS]
				WHERE [Tier] = 'SNRFOR'  AND (Date < '03/21/2011') AND (Date >= '09/20/2010')  AND [Mnemonic] in 
					('Advanced Micro Devices Inc',
						'AK Stl Corp',
						'Alcatel Lucent USA Inc',
						'ALLTEL Corp',
						'Ally Finl Inc',
						'Ambac Finl Gp Inc',
						'Amern Axle & Mfg Inc',
						'Amern Gen Fin Corp',
						'Amkor Tech Inc',
						'AMR Corp',
						'ARAMARK Corp',
						'Archstone',
						--'Argentine Rep',
						'ArvinMeritor Inc',
						'Ashland Inc',
						'Assur Gty Mun Corp',
						'AVIS BUDGET CAR Rent LLC',
						'Avis Budget Group Inc',
						'Ball Corp',
						'Bausch & Lomb Inc',
						'Beazer Homes USA Inc',
						'Belo Corp.',
						'Block Finl LLC',
						'Bombardier Cap Inc',
						'Bombardier Inc',
						'Boyd Gaming Corp',
						'Brunswick Corp',
						'CA St',
						'Caesars Entmt Corp',
						'Celestica Inc',
						'Chesapeake Engy Corp',
						'Clear Channel Comms Inc',
						'Cmnty Health Sys Inc',
						'Constellation Brands Inc',
						'Cooper Tire & Rubr Co',
						'CSC Hldgs LLC',
						'D R Horton Inc',
						'Dean Foods Co',
						--'Delhaize America LLC',
						'Delta Air Lines Inc',
						'Deluxe Corp',
						'Dillards Inc',
						'DISH DBS Corp',
						'Dole Food Co Inc',
						'Domtar Corp',
						'Dynegy Hldgs Inc',
						'Eastman Kodak Co',
						'El Paso Corp',
						'Energy Future Hldgs Corp',
						'Entergy Corp',
						'Flextronics Corp',
						'Flextronics Intl Ltd',
						'Ford Mtr Co',
						'FORD Mtr Cr Co LLC',
						'FPL GROUP Cap INC',
						'Freescale Semiconductor Inc',
						'Frontier Comms Corp',
						'Fst Oil Corp',
						'GA PACIFIC LLC',
						'Gannett Co Inc DE',
						'Gen Mtrs Co',
						'Goodyear Tire & Rubr Co',
						'Harrahs Oper Co Inc',
						'HCA Inc.',
						'Health Mgmt Assoc Inc',
						'Hertz Corp',
						'HILTON WORLDWIDE INC',
						'Host Hotels & Resorts LP',
						'HUNTSMAN Intl LLC',
						'IKON Office Solutions Inc',
						'Intelsat SA',
						'Interpublic Gp Cos Inc',
						'Iron Mtn Inc',
						'Istar Finl Inc',
						'J C Penney Co Inc',
						'Jones Apparel Gp Inc',
						'Jones Group Inc',
						'K Hovnanian Entpers Inc',
						'KB Home',
						--'Kinder Morgan Inc',
						'LA Pac Corp',
						'Lennar Corp',
						'Level 3 Comms Inc',
						'Levi Strauss & Co',
						'Liberty Media LLC',
						'Liberty Mutual Group Inc',
						'Liz Claiborne Inc',
						'Ltd Brands Inc',
						'Macy s Inc',
						'Macy s Retail Hldgs Inc',
						'Massey Engy Co',
						'MBIA Inc.',
						'MBIA Ins Corp',
						'McClatchy Co',
						'Mediacom LLC',
						'MGIC Invt Corp',
						'MGM Resorts Intl',
						'Mirant North America LLC',
						'Mohawk Inds Inc',
						'NALCO Co',
						'Neiman Marcus Gp Inc',
						'New Albertson s Inc',
						'Nextel Comms Inc',
						'Norbord Inc',
						'NOVA Chems Corp',
						'NRG Energy Inc',
						'NY Times Co',
						'Office Depot Inc',
						'Olin Corp',
						'Omnicare Inc',
						'Owens IL Inc',
						'Parker Drilling Co',
						'Peabody Engy Corp',
						'PHH Corp',
						'Pioneer Nat Res Co',
						'PMI Gp Inc',
						'Polyone Corp',
						'PulteGroup Inc',
						'Qwest Cap Fdg Inc',
						'Qwest Corp',
						'Radian Gp Inc',
						'RadioShack Corp',
						'Realogy Corp',
						'Residential Cap LLC',
						'Rite Aid Corp',
						--'Rogers Comms Inc',
						'Royal Caribbean Cruises Ltd',
						'RRI Energy Inc',
						'Ryland Gp Inc',
						'Sabre Hldgs Corp',
						'Saks Inc',
						'Sanmina SCI Corp',
						'Seagate Tech HDD Hldgs',
						'Sealed Air Corp US',
						'Sears Roebuck Accep Corp',
						'ServiceMaster Co',
						'Smithfield Foods Inc',
						'Sprint Nextel Corp',
						'St IL',
						--'St MI',
						'Starwood Hotels & Resorts Wwide Inc',
						'Std Pac Corp',
						'SUNGARD DATA Sys INC',
						'SUPERVALU INC',
						'Tenet Healthcare Corp',
						'Tesoro Corp',
						'Textron Finl Corp',
						'Textron Inc',
						'The AES Corp',
						'Toys R Us Inc',
						'Transocean Worldwide Inc',
						'TRW Automotive Inc',
						'TX Competitive Elec Hldgs Co LLC',
						'Unisys Corp',
						'Univision Comms Inc',
						'Unvl Health Svcs Inc',
						'Utd Rents North Amer Inc',
						'Utd Sts Stl Corp',
						'Wendys Intl Inc',
						'Windstream Corp'
						)"""

		cds_individual_portfolio = CDS()
		cds_individual_portfolio.connect_db(sql_CDS)
		cds_individual_portfolio.cds_data_transform(100)	
		df_clean = cds_individual_portfolio.df

	elif cds_input == 13:
		sql_CDS = """SELECT [Date],[Mnemonic] as Ticker,[RedCode],[Tier],[Ccy],[DocClause],[Contributor],[Spread5y],[Recovery],[CompositeCurveRating],[Sector],[Region],[Country],[AvRating],[ImpliedRating] FROM [hobbit].[dbo].[CDS]
				WHERE [Tier] = 'SNRFOR'  AND (Date < '03/21/2011') AND (Date >= '09/20/2010')  AND [Mnemonic] in 
					('Zurich Ins Co Ltd',
						'YORKSHIRE WATER SERVICES Fin Ltd',
						'WPP 2005 Ltd',
						'Xstrata Plc',
						'Wolters Kluwer N V',
						'WestLB AG',
						'Veolia Environnement',
						'Vinci',
						'Vivendi',
						'Vodafone Gp PLC',
						'Volkswagen AG',
						'Vattenfall AB',
						--'Utd Business Media Ltd',
						--'Utd Kdom Gt Britn & Nthn Irlnd',
						'Telekom Austria AG',
						'Telekom Polska SA',
						'Telenor ASA',
						'TeliaSonera AB',
						'Tesco PLC',
						'THALES',
						--'TNT N.V.',
						'THOMSON REUTERS GROUP Ltd',
						'Utd Utils plc',
						'Utd Utils Wtr plc',
						--'Utd Sts Amer',
						'Total SA',
						'UNIBAIL RODAMCO SE',
						'UniCredit Bk AG',
						'UniCredit SpA',
						'Unilever N V',
						'Unipol Gruppo Finanziario SpA',
						'UBS AG',
						'Telecom Italia SpA',
						'TelefonAB L M Ericsson',
						'Telefonica S A',
						'Tate & Lyle PLC',
						'Technip',
						'Swiss Reins Co Ltd',
						'Swisscom AG',
						'Syngenta AG',
						'Svenska Cellulosa AB SCA',
						'Svenska Handelsbanken AB',
						'Swedish Match AB',
						'Stmicroelectronics N V',
						'Suedzucker AG',
						'Skandinaviska Enskilda Banken AB',
						'Siemens AG',
						--'SANOFI AVENTIS',
						'SANTANDER UK PLC',
						'Societe Generale',
						'Societe Television Francaise 1',
						'SODEXO',
						'Smiths Gp Plc',
						--'Slovak Rep',
						--'St Israel',
						'Solvay SA',
						'Statoil ASA',
						'Std Chartered Bk',
						--'St Qatar',
						'STANDARD LIFE Assurn Ltd',
						'Roche Hldgs Inc',
						'Rexam plc',
						--'Rep Latvia',
						--'Rep Lithuania',
						'Repsol YPF SA',
						--'Rep Irlnd',
						--'Rep Italy',
						--'Rep Kazakhstan',
						--'Rep Croatia',
						--'Rep Cyprus',
						--'Rep Estonia',
						--'Rep Finland',
						--'Rep Hungary',
						--'Rep Iceland',
						--'Rep Poland',
						--'Rep Portugal',
						--'Rep Slovenia',
						--'Rep South Africa',
						'SAFEWAY LTD',
						'SABMiller PLC',
						'ROYAL DUTCH SHELL PLC',
						--'Russian Agric Bk',
						--'Russian Fedn',
						'RWE AG',
						--'Rolls Royce plc',
						'Royal & Sun Alliance Ins PLC',
						'Royal Bk of Scotland NV',
						--'Royal Bk Scotland plc',
						'SES',
						'Securitas AB',
						'Schneider Elec SA',
						'SCOR SE',
						'SCOTTISH & NEWCASTLE Ltd',
						'Scottish & Sthn Engy plc',
						--'SBERBANK',
						'SCANIA AB',
						'Reed Elsevier PLC',
						'Rentokil Initial 1927 Plc',
						'RENTOKIL INITIAL PLC',
						--'Rep Austria',
						--'Rep Bulgaria',
						'Raiffeisen Zentralbank Oesterreich AG',
						'Rabobank Nederland',
						'Pernod Ricard',
						'PPR',
						'Publicis Groupe SA',
						'Prudential PLC',
						'mmO2 PLC',
						'Old Mut plc',
						'Pearson plc',
						'Portugal Telecom Intl Fin B V',
						'Natl Grid Plc',
						'Merck KGaA',
						'Nestle S A',
						'Next plc',
						'Nokia Oyj',
						'Novartis AG',
						'Nordea Bk AB',
						'Natixis',
						'Munich Re',
						'METRO AG',
						'Metso Corp',
						'Mediobanca SpA',
						'Marks & Spencer p l c',
						'Man Gp plc',
						'Lloyds TSB Bk plc',
						--'Lukoil Co',
						'LVMH Moet Hennessy Louis Vuitton',
						'L AIR LIQUIDE SA POUR LTDE EXPLTN PROCDS GEORGS CLDE',
						'La C de Aho y Pensiones de Barcelona',
						--'Lafarge',
						'Lanxess',
						'Legal & Gen Gp PLC',
						'Linde AG',
						'KELDA GROUP Ltd',
						'Klepierre',
						'Koninklijke Ahold N V',
						'Koninklijke DSM NV',
						'Koninklijke KPN N V',
						'Koninklijke Philips Electrs N V',
						'Kingfisher PLC',
						--'Kdom Belgium',
						--'Kdom Denmark',
						--'Kdom Neth',
						--'Kdom Norway',
						--'Kdom Saudi Arabia',
						--'Kdom Spain',
						--'Kdom Sweden',
						'Holcim Ltd',
						'Iberdrola Intl BV',
						--'Iberdrola S A',
						'HSBC Bk plc',
						'Intesa Sanpaolo SpA',
						'IMPERIAL Chem Inds Ltd',
						'Imperial Tob Gp PLC',
						'ING Bk N V',
						'ING Verzekeringen NV',
						'IKB Deutsche Industriebank AG',
						--'Israel Elec Corp LTD',
						'Inv AB',
						'Invensys plc',
						'J Sainsbury PLC',
						--'JSC GAZPROM',
						--'JSC VTB Bk',
						'JTI UK Fin PLC',
						'GROUPE AUCHAN',
						'Gov & Co Bk Irlnd',
						'Glaxosmithkline Plc',
						'Glencore Intl AG',
						'Hannover Ruck AG',
						'Hammerson PLC',
						'HBOS Plc',
						'Heineken NV',
						--'Hellenic Telecom Org SA',
						'Henkel AG & Co KGaA',
						--'French Rep',
						'Gas Nat SDG SA',
						'GDF SUEZ',
						'France Telecom',
						--'Fed Rep Germany',
						'ENI S.p.A.',
						'Fortum Oyj',
						'Finmeccanica S p A',
						'Daimler AG',
						'DANONE',
						'Danske Bk A S',
						'Deutsche Bahn AG',
						'Deutsche Bk AG',
						--'Deutsche Lufthansa AG',
						'Deutsche Post AG',
						'Deutsche Telekom AG',
						--'Dubai Govt',
						'DONG ENERGY A S',
						'DNB NOR Bk ASA',
						'Dexia Cr Loc',
						'Diageo PLC',
						'EXPERIAN Fin PLC',
						'Erste Group Bk AG',
						'Essent N V',
						'Eurpn Aero Defence & Space Co Eads N V',
						'Endesa S A',
						'ENEL S p A',
						'EnBW Energie Baden Wuerttemberg AG',
						--'Emirate of Abu Dhabi',
						'Elisa Oyj',
						'ELECTRICITE DE FRANCE',
						'Edison S p A',
						--'EDP Energias de Portugal SA',
						'E.ON AG',
						'Cr Agricole SA',
						'Credit Suisse Gp Ltd',
						--'Czech Rep',
						'Commerzbank AG',
						'Compass Gp PLC',
						'Clariant AG',
						'Carrefour',
						--'Casino Guichard Perrachon',
						'Carlsberg Breweries A S',
						'Cap Gemini',
						'Caixa Geral de Depositos S A',
						'Centrica plc',
						'Cie de St Gobain',
						'CIE Fin Michelin',
						'ALSTOM',
						'ALTADIS SA',
						'Alliander NV',
						'Allianz SE',
						'Allied Irish Bks PLC',
						--'AKZO Nobel N V',
						'ageas N.V.',
						'Aegon N.V.',
						'ACS Actividades Construccion y Servicios SA',
						'Adecco S A',
						--'Abu Dhabi Natl Energy Co PJSC',
						'ACCOR',
						'3i Gp plc',
						'AB Electrolux',
						'AB SKF',
						'AB Volvo',
						'ABB Intl Fin Ltd',
						'Anheuser Busch InBev NV',
						'Anglo Amern plc',
						'ATLANTIA SPA',
						'Atlas Copco AB',
						'Astrazeneca PLC',
						'ArcelorMittal',
						'ARCELORMITTAL FRANCE',
						'ASSA ABLOY AB',
						'Assicurazioni Generali S p A',
						'BASF Schweiz AG',
						'BASF SE',
						'Bertelsmann AG',
						'Bco Bilbao Vizcaya Argentaria S A',
						'Bco Comercial Portugues SA',
						'Bco de Sabadell S A',
						'Bco Espirito Santo S A',
						'Bco Pop Espanol',
						'Bco Pop S C',
						'Bco SANTANDER SA',
						'Bay Landbk Giroz',
						'Bay Motoren Werke AG',
						'Bayer AG',
						'Bca Monte dei Paschi di Siena S p A',
						'Bca Pop di Milano Soc Coop a r l',
						'Bankinter S A',
						'Barclays Bk plc',
						'AXA',
						'BAA Fdg Ltd',
						'BAE Sys PLC',
						'Aviva plc',
						--'BRISA Fin BV',
						'BNP Paribas',
						'Brit Amern Tob plc',
						'Brit Sky Broadcasting Gp PLC',
						'Brit Telecom PLC',
						'CADBURY Hldgs Ltd',
						'C de Aho Vlncia Castlln Alicnte Bcaja',
						'C de Aho Y Monte de Piedad de Madrid',
						'Bk OF SCOTLAND PLC',
						'BP P.L.C.',
						--'Bqe Cen de Tunisie',
						'Bqe Federative Du Cr Mutuel',
						'BOUYGUES',
						'Evonik Degussa GmbH',
						'Fortis Bk',
						'HANSON Ltd',
						'PILKINGTON GROUP Ltd',
						'Porsche Automobil Hldg SE'

						)"""

		cds_individual_portfolio = CDS()
		cds_individual_portfolio.connect_db(sql_CDS)
		cds_individual_portfolio.cds_data_transform(100)	
		df_clean = cds_individual_portfolio.df

	elif cds_input == 14:
		sql_CDS = """SELECT [Date],[Mnemonic] as Ticker,[RedCode],[Tier],[Ccy],[DocClause],[Contributor],[Spread5y],[Recovery],[CompositeCurveRating],[Sector],[Region],[Country],[AvRating],[ImpliedRating] FROM [hobbit].[dbo].[CDS]
				WHERE [Tier] = 'SNRFOR'  AND (Date < '03/21/2011') AND (Date >= '09/20/2010')  AND [Mnemonic] in 
					('Wind Acquisition Fin SA',
						'WENDEL',
						'VIRGIN MEDIA Fin PLC',
						'Valeo',
						'ProSiebenSat 1 Media AG',
						'TUI AG',
						'ThyssenKrupp AG',
						'UPC Broadband Hldg BV',
						'UPC Hldg BV',
						'UPM Kymmene CORP',
						'Unitymedia GmbH',
						'Tomkins Ltd',
						'Tomkins plc',
						--'Ukraine',
						'TDC A/S',
						'Stena Aktiebolag',
						'Stora Enso CORP',
						'SOCIETE AIR FRANCE',
						'Smurfit Kappa Fdg plc',
						'SOL MELIA S A',
						'Rhodia',
						'REXEL Dev SAS',
						--'Rep Turkey',
						--'Romania',
						'Seat Pagine Gialle SpA',
						'Scandinavian Airls Sys DNS',
						'Renault',
						'Rallye',
						'Rank Gp PLC',
						'ONO Fin II plc',
						'Peugeot SA',
						--'Porsche Automobil Hldg SE',
						--'PILKINGTON GROUP Ltd',
						'Nielsen Co',
						'NXP B.V.',
						'Norske Skogindustrier ASA',
						'M real Corp',
						'LADBROKES PLC',
						--'Lebanese Rep',
						'ITV Plc',
						'Kazkommertsbank JSC',
						'Ineos Gp Hldgs plc',
						'Infineon Tech Hldg B V',
						'ISS Glob A S',
						--'ISS Hldg A S',
						'Intl Pwr PLC',
						'Irish Life & Perm plc',
						'Kabel Deutschland GmbH',
						'Grohe Hldg Gmbh',
						'GKN Hldgs plc',
						--'HANSON Ltd',
						'Havas',
						'HeidelbergCement AG',
						--'Hellenic Rep',
						'FKI plc',
						--'Fresenius SE',
						'Gecina',
						'FCE Bk PLC',
						--'Fortis Bk',
						'FIAT S p A',
						'DSG Intl PLC',
						'Dixons Retail plc',
						--'Evonik Degussa GmbH',
						'ERC IRELAND Fin Ltd',
						'EMI Group Ltd',
						'EIRCOM Ltd',
						'CORUS GROUP Ltd',
						'Contl AG',
						'COLT Tech SERVICES GROUP Ltd',
						'CODERE Fin LUXEMBOURG SA',
						'Cognis GmbH',
						'CARLTON Comms Ltd',
						'CIR SpA CIE Industriali Riunite',
						'Alliance Boots Hldgs Ltd',
						'ALLIED DOMECQ LTD',
						'Alcatel Lucent',
						--'Arab Rep Egypt',
						'Angel Lux Com S.A.',
						'Anglo Irish Bk Corp Ltd',
						'Brit Awys plc',
						'Cable & Wireless PLC',
						'CABLE WIRELESS LTD',
						'Deutsche Lufthansa AG',
						'Hellenic Telecom Org SA',
						'Lafarge'

						)"""

		cds_individual_portfolio = CDS()
		cds_individual_portfolio.connect_db(sql_CDS)
		cds_individual_portfolio.cds_data_transform(100)	
		df_clean = cds_individual_portfolio.df

	elif cds_input == 15:
			sql_CDS = """SELECT [Date],[Mnemonic] as Ticker,[RedCode],[Tier],[Ccy],[DocClause],[Contributor],[Spread5y],[Recovery],[CompositeCurveRating],[Sector],[Region],[Country],[AvRating],[ImpliedRating] FROM [hobbit].[dbo].[CDS]
				WHERE [Tier] = 'SNRFOR'  AND (Date < '03/20/2018') AND (Date >= '09/20/2017') AND [Mnemonic] in 
					('21st Century Fox America Inc',
					'3M Co',
					'Abbott Labs',
					'ADARKO PETROLEUM CORP',
					'Aetna Inc.',
					--'Agrium Inc',
					'Allstate Corp',
					'ALLTEL Corp',
					'Altria Gp Inc',
					'Amern Elec Pwr Co Inc',
					'Amern Express Co',
					'Amern Intl Gp Inc',
					'Amgen Inc.',
					'Andeavor',
					'APACHE CORP',
					'ARROW ELECTRS INC',
					'Assur Gty Corp',
					'AT&T Inc',
					'Autozone Inc',
					'Avalon Bay Cmntys Inc',
					'Avnet Inc',
					'Baker Hughes a GE Co LLC',
					'Barrick Gold Corp',
					'Baxter Intl Inc',
					'Beam Suntory Inc',
					'Berkshire Hathaway Inc',
					'Best Buy Co Inc',
					'Bk of America Corp',
					'Boeing Cap Corp',
					'BOEING CO',
					'BorgWarner Inc',
					'Boston Pptys Ltd Partnership',
					'Boston Scientific Corp',
					'Bristol Myers Squibb Co',
					'Brunswick Corp',
					'Burlington Nthn Santa Fe Corp',
					'CA Inc',
					'CAMPBELL SOUP CO',
					'Cap One Finl Corp',
					'Cap One Finl Corp',
					'Cardinal Health Inc',
					'Carnival Corp',
					'Caterpillar Finl Svcs Corp',
					'Caterpillar Inc',
					'CBS Corp',
					'CDN NAT RES LTD',
					'Cdn Natl Rwy Co',
					'Chevron Corp',
					'Chubb INA Hldgs Inc',
					'Chubb Ltd',
					'Cisco Sys Inc',
					'Citigroup Inc',
					'CMS Engy Corp',
					'CNA Finl Corp',
					'COCACOLA CO',
					'Comcast Corp',
					'Conagra Brands Inc',
					'ConocoPhillips',
					'Constellation Brands Inc',
					'Corning Inc',
					'Cox Comms Inc',
					'CSX Corp',
					'CVS Health Corp',
					'Cytec Inds Inc',
					'D R Horton Inc',
					'Darden Restaurants Inc',
					'DDR Corp',
					'Deere & Co',
					'Delta Air Lines Inc',
					'Devon Engy Corp',
					'Dominion Energy Inc',
					'Domtar Corp',
					'Dow Chem Co',
					'Duke Energy Carolinas LLC',
					'DXC TECH CO',
					'E I du Pont de Nemours & Co',
					'Eastman Chem Co',
					'Eli Lilly & Co',
					'Enbridge Inc',
					'EnCana Corp',
					-- No data for the test period
					--'ENERGY TRANSFER LP',
					'ERP Oper Ltd Pship',
					'Exelon Corp',
					'Exelon Generation Co LLC',
					'Expedia Group Inc',
					'FirstEnergy Corp',
					'FIS DATA SYSS INC',
					'FMC Corp',
					'Ford Mtr Co',
					'G A T X Corp',
					'Gen Elec Co',
					'Gen Mls Inc',
					'Gen Mtrs Corp',
					'Goldman Sachs Gp Inc',
					'Goodrich Corp',
					'H & R Block Inc',
					'Halliburton Co',
					'HARTFORD FINL SERVICES GROUP INC',
					'Hasbro Inc',
					'HCP INC',
					'Hershey Co',
					'Hess Corp',
					'Hillshire Brands Co',
					'Home Depot Inc',
					'Honeywell Intl Inc',
					'Host Hotels & Resorts Inc',
					'HP Inc',
					'HSBC Fin Corp',
					'Humana Inc',
					'Ingersoll Rand Co Ltd',
					'Interpublic Gp Cos Inc',
					'Intl Business Machs Corp',
					'INTL LEASE FIN CORP',
					'Intl Paper Co',
					'Johnson & Johnson',
					'JOHNSON CTLS INTL PUB LTD CO',
					'JPMorgan Chase & Co',
					'KIMBERLYCLARK CORP',
					'Kimco Rlty Corp',
					'Kinder Morgan Engy Partners L P',
					'Kinder Morgan Inc.',
					'Kohls Corp',
					'Kraft Heinz Foods Co',
					'Lincoln Natl Corp',
					'Lockheed Martin Corp',
					'Loews Corp',
					'Lowes Cos Inc',
					'Macy s Inc',
					'Marathon Oil Corp',
					'Marriott Intl Inc',
					'Marsh & Mclennan Cos Inc',
					'Masco Corp',
					'McDONALDS Corp',
					'McKesson Corp',
					'Medtronic Inc',
					'Merck Sharp & Dohme Corp',
					'MetLife Inc',
					'Mohawk Inds Inc',
					'Mondelez Intl Inc',
					'Morgan Stanley',
					'Motorola Solutions Inc',
					'Natl Rural Utils Coop Fin Corp',
					'Newell Brands Inc',
					'Newmont Mng Corp',
					'NextEra Energy Cap Hldgs Inc',
					'NiSource Inc',
					'Noble Engy Inc',
					'Noble Engy Inc',
					'Nordstrom Inc',
					'Norfolk Sthn Corp',
					'Northrop Grumman Corp',
					'Nucor Corp',
					'OCCIDENTAL PETROLEUM CORP',
					'Omnicom Gp Inc',
					'ONEOK INC',
					'Packaging Corp Amer',
					'Pepsico Inc',
					'Pfizer Inc',
					'Pioneer Nat Res Co',
					'Pitney Bowes Inc',
					'PLAINS ALL Amern PIPELINE LP',
					'PPG Inds Inc',
					'Procter & Gamble Co',
					'Prologis LP',
					'Prudential Finl Inc',
					'Quest Diagnostics Inc',
					'Raytheon Co',
					'Rep Svcs Inc',
					'Reynolds Amern Inc',
					'Roche Hldgs Inc',
					'Rohm & Haas Co',
					'Royal Caribbean Cruises Ltd',
					'RPM Intl Inc',
					'Ryder Sys Inc',
					'Sempra Engy',
					'Sherwin Williams Co',
					'Simon Ppty Gp L P',
					'Smithfield Foods Inc',
					'Southwest Airls Co',
					'Spectra Energy Cap LLC',
					'Stanley Black & Decker Inc',
					'Sunoco Inc',
					'Target Corp',
					'TEXTRON INC',
					'The Kroger Co.',
					'Time Warner Inc',
					'TransCanada Pipelines Ltd',
					'Travelers Cos Inc',
					'Tyson Foods Inc',
					'Un Pac Corp',
					'UnitedHealth Gp Inc',
					'Unum Group',
					'Utd Parcel Svc Inc',
					--'Vale SA',
					'Valero Energy Corp',
					'Verizon Comms Inc',
					'Viacom',
					'Vulcan Matls Co',
					'WALMART INC',
					'Walt Disney Co',
					'Waste Mgmt Inc',
					'Wells Fargo & Co',
					'Westn Un Co',
					'WestRock RKT Co',
					'Weyerhaeuser Co',
					'Whirlpool Corp',
					'Xerox Corp',
					'XLIT Ltd')"""

			cds_individual_portfolio = CDS()
			cds_individual_portfolio.connect_db(sql_CDS)
			cds_individual_portfolio.cds_data_transform(100)	
			df_clean = cds_individual_portfolio.df

	elif cds_input == 16:
			sql_CDS = """SELECT [Date],[Mnemonic] as Ticker,[RedCode],[Tier],[Ccy],[DocClause],[Contributor],[Spread5y],[Recovery],[CompositeCurveRating],[Sector],[Region],[Country],[AvRating],[ImpliedRating] FROM [hobbit].[dbo].[CDS]
				WHERE [Tier] = 'SNRFOR'  AND (Date < '03/20/2018') AND (Date >= '09/20/2017') AND [Mnemonic] in
				('1st Data Corp',
						'ADT SEC CORP',
						'Advanced Micro Devices Inc',
						'AK Stl Corp',
						'Ally Finl Inc',
						'Amern Airls Group Inc',
						'Amern Axle & Mfg Hldgs Inc',
						'Amkor Tech Inc',
						'ARAMARK Services Inc',
						'Arconic Inc.',
						'Avis Budget Group Inc',
						'Avon Prods Inc',
						'Ball Corp',
						'Bausch Health Cos Inc',
						'BEAZER HOMES USA INC',
						'BOMBARDIER INC.',
						'Boyd Gaming Corp',
						'CA RES CORP',
						'Cablevision Sys Corp',
						--'CalAtlantic Group Inc',
						'Calpine Corp',
						'CCO Hldgs LLC',
						--'CEMEX S A Bursatil Cap Variable',
						'CenturyLink Inc',
						'Chesapeake Engy Corp',
						'CIT Gp Inc',
						'Cmnty Health Sys Inc',
						'Coml Metals Co',
						'Cooper Tire & Rubr Co',
						'CSC Hldgs LLC',
						'DaVita Inc',
						'Dean Foods Co',
						'Dell Inc',
						'DELUXE CORP',
						'Diamond Offshore Drilling Inc',
						'Dillards Inc',
						'DISH DBS Corp',
						--'Dynegy Inc',
						'Embarq Corp',
						'FreeportMcMoRan Inc',
						'Frontier Comms Corp',
						'GAP INC',
						'Genworth Hldgs Inc',
						'Goodyear Tire & Rubr Co',
						'HCA Inc.',
						'HD SUPPLY INC',
						'HERTZ CORP',
						'Hovnanian Entpers Inc',
						'HUNTSMAN Intl LLC',
						'Iron Mtn In',
						'iStar Inc',
						'J C Penney Co Inc',
						'KB HOME',
						'L Brands Inc',
						'LA Pac Corp',
						'Lamb Weston Hldgs Inc',
						'Lennar Corp',
						'Levi Strauss & Co',
						'Lexmark Intl Inc',
						'Liberty Interactive LLC',
						'M D C Hldgs Inc',
						'Mattel Inc',
						'MBIA Inc.',
						'McClatchy Co',
						'Meritor Inc',
						'MGIC Invt Corp',
						'MGM Growth Pptys Oper Partnership LP',
						'MGM Resorts Intl',
						'Murphy Oil Corp',
						'Nabors Inds Inc',
						'Navient Corp',
						'Neiman Marcus Group LLC',
						'New Albertsons LP',
						'New York Times Co',
						--'Nine West Hldgs Inc',
						--'Noble Group Ltd',
						'Norbord Inc',
						'NOVA Chems Corp',
						'NRG Energy Inc',
						'Office Depot Inc',
						'Olin Corp',
						'Owens IL Inc',
						'Pactiv LLC',
						'Parker Drilling Co',
						'PHH Corp',
						'Polyone Corp',
						'PulteGroup Inc',
						'R R Donnelley & Sons Co',
						'Radian Gp Inc',
						'Realogy Group LLC',
						'Rite Aid Corp',
						'Sabre Hldgs Corp',
						'Safeway Inc',
						'Sanmina Corp',
						'Sealed Air Corp US',
						'SEARS ROEBUCK Accep CORP',
						'Springleaf Fin Corp',
						'Sprint Comms Inc',
						'Staples Inc',
						'SUPERVALU INC',
						'T Mobile USA Inc',
						'Talen Energy Supply LLC',
						'Targa Res Partners LP',
						'Teck Res Ltd',
						'TEGNA Inc',
						'Tenet Healthcare Corp',
						'The AES Corp',
						'Toll Bros Inc',
						'Transdigm Inc',
						'Unisys Corp',
						'Uniti Group Inc',
						'Univision Comms Inc',
						'Unvl Health Svcs Inc',
						'Utd Continental Hldgs Inc',
						'Utd Sts Stl Corp',
						'Wendys Intl LLC',
						'Whiting Petroleum Corp',
						'WILLIAMS COS INC',
						'Windstream Services LLC',
						'YUM Brands Inc',
						-- Added July 5th
						'Weatherford International Ltd.')

			"""

			cds_individual_portfolio = CDS()
			cds_individual_portfolio.connect_db(sql_CDS)
			cds_individual_portfolio.cds_data_transform(100)	
			df_clean = cds_individual_portfolio.df

	elif cds_input == 17:
			sql_CDS = """SELECT [Date],[Mnemonic] as Ticker,[RedCode],[Tier],[Ccy],[DocClause],[Contributor],[Spread5y],[Recovery],[CompositeCurveRating],[Sector],[Region],[Country],[AvRating],[ImpliedRating] FROM [hobbit].[dbo].[CDS]
				WHERE [Tier] = 'SNRFOR'  AND (Date < '03/20/2018') AND (Date >= '09/20/2017') AND [Mnemonic] in
				('AB Electrolux',
						'AB Volvo',
						'ABERTIS INFRAESTRUCTURAS SA',
						'ACCOR',
						'Adecco Group AG',
						'Aegon N.V.',
						'Airbus SE',
						'Akzo Nobel NV',
						'Alliance Boots Hldgs Ltd',
						'Allianz SE',
						'ALSTOM',
						'Anglo Amern plc',
						'AnheuserBusch InBev',
						'Assicurazioni Generali S p A',
						'Astrazeneca PLC',
						'ATLANTIA SPA',
						'Auchan Hldg',
						'Aviva plc',
						'AXA',
						'BAE Sys PLC',
						'BANKIA SA',
						'Bankinter S A',
						'Barclays Bk plc',
						'Barclays PLC',
						'BASF SE',
						'Bay Landbk Giroz',
						'Bay Motoren Werke AG',
						'Bayer AG',
						'Bco Bilbao Vizcaya Argentaria S A',
						'Bco de Sabadell S A',
						'Bco Pop Espanol',
						'Bco SANTANDER SA',
						'Beni Stabili',
						'Bertelsmann SE Co KGaA',
						'Bk OF SCOTLAND PLC',
						'BNP Paribas',
						'BOUYGUES',
						'BP P.L.C.',
						'BRISA CONCESSAO RODOVIARIA SA',
						'Brit Amern Tob plc',
						'Brit Awys plc',
						'Brit Sky Broadcasting Gp PLC',
						'Brit Telecom PLC',
						'CaixaBank SA',
						'CAPGEMINI',
						'Carlsberg Breweries A S',
						'Carrefour',
						'CECONOMY AG',
						'Centrica plc',
						'Cie de St Gobain',
						'CIE GENERALE des ETABLISSEMENTS MICHELIN',
						'Clariant AG',
						'CNH Indl NV',
						'Commerzbank AG',
						'Compass Gp PLC',
						'Contl AG',
						'Cooeperatieve Rabobank UA',
						'Cr Agricole SA',
						'Cr Suisse AG',
						'Daimler AG',
						'DANONE',
						'Danske Bk A S',
						'Deutsche Bahn AG',
						'Deutsche Bk AG',
						'Deutsche Lufthansa AG',
						'Deutsche Post AG',
						'Deutsche Telekom AG',
						'Dexia',
						'Diageo PLC',
						'DNB Bk ASA',
						'EDP Energias de Portugal SA',
						'EDP Energias de Portugal SA',
						'Electricite de France',
						'EnBW Energie Baden Wuerttemberg AG',
						'ENEL S p A',
						'ENGIE',
						'ENI S.p.A.',
						'EON SE',
						'Erste Group Bk AG',
						'EXPERIAN Fin PLC',
						'Fortum Oyj',
						'Fresenius SE & Co KGaA',
						'Gecina',
						'Glaxosmithkline Plc',
						'Glencore Intl AG',
						'Hammerson PLC',
						'Hannover Rueck SE',
						'HeidelbergCement AG',
						'Heineken NV',
						'Henkel AG & Co KGaA',
						'Hochtief AG',
						'HSBC Bk plc',
						'HSBC Hldgs plc',
						'Iberdrola SA',
						'IMPERIAL BRANDS PLC',
						'ING Bk N V',
						'innogy SE',
						'Intesa Sanpaolo SpA',
						'ISS AS',
						'ITV Plc',
						'Kering',
						'Kingfisher PLC',
						'Koninklijke Ahold Delhaize NV',
						'Koninklijke DSM NV',
						'Koninklijke KPN N V',
						'Koninklijke KPN N V',
						'LafargeHolcim Ltd',
						'LAIR LIQUIDE SOCIETE ANONYME POUR LETUDE ET LEXPLOITATION DES PROCEDES GEORGES CLAUDE',
						'Landbk Baden Wuertbg',
						'Lanxess',
						'Legal & Gen Gp PLC',
						'Linde AG',
						'LLOYDS BK PLC',
						'Lloyds Bkg Group plc',
						'LVMH Moet Hennessy Louis Vuitton',
						'MARKS & SPENCER GROUP PLC',
						'Mediobanca SpA',
						'Merck KGaA',
						'Metso Corp',
						'Munich Re',
						'Nationwide Bldg Soc',
						'Natl Grid Plc',
						'Nestle S A',
						'Next plc',
						'Nordea Bnk AB',
						'Novartis AG',
						'Old Mut plc',
						'Orange',
						'Pearson plc',
						'Pernod Ricard',
						'Porsche Automobil Hldg SE',
						'PostNL NV',
						'Prudential Finl Inc',
						'Publicis Groupe SA',
						'Raiffeisen Bk Intl AG',
						'RELX PLC',
						'Renault',
						'RENTOKIL INITIAL PLC',
						'REPSOL SA',
						'Rodamco Europe NV',
						'Rolls Royce plc',
						'Royal Bk Scotland Gp PLC',
						'Royal Bk Scotland Gp PLC',
						'ROYAL DUTCH SHELL PLC',
						'SANOFI',
						'Schaeffler Fin BV',
						'SES',
						'Siemens AG',
						'Skandinaviska Enskilda Banken AB',
						'Societe Generale',
						'SODEXO',
						'Solvay SA',
						'SSE PLC',
						'Std Chartered Bk',
						'Stmicroelectronics N V',
						'Suedzucker',
						'Svenska Handelsbanken AB',
						'Swedbank AB',
						'Swedish Match AB',
						'Swiss Reins Co Ltd',
						'Tate & Lyle PLC',
						'TechnipFMC PLC',
						'Telefonica S A',
						'Telekom Austria AG',
						'Telenor ASA',
						'Telia Co AB',
						'THALES',
						'Total SA',
						'UBS AG',
						'UBS Group AG',
						'UniCredit Bk AG',
						'UniCredit SpA',
						'Unilever N V',
						'Unione di Banche Italiane S per azioni',
						'UPM Kymmene CORP',
						'Utd Utils plc',
						'Valeo',
						'Vattenfall',
						'Veolia Environnement',
						'Vinci',
						'Vivendi',
						'Vodafone Gp PLC',
						'Volkswagen AG',
						'WENDEL',
						'Wolters Kluwer N V',
						'WPP 2005 Ltd',
						'Zurich Ins Co Ltd',
						-- Added on July 5th
						'Koninklijke Philips NV',
						'SAFEWAY LIMITED')

			"""

			cds_individual_portfolio = CDS()
			cds_individual_portfolio.connect_db(sql_CDS)
			cds_individual_portfolio.cds_data_transform(100)	
			df_clean = cds_individual_portfolio.df

	elif cds_input == 18:
			sql_CDS = """SELECT [Date],[Mnemonic] as Ticker,[RedCode],[Tier],[Ccy],[DocClause],[Contributor],[Spread5y],[Recovery],[CompositeCurveRating],[Sector],[Region],[Country],[AvRating],[ImpliedRating] FROM [hobbit].[dbo].[CDS]
				WHERE [Tier] = 'SNRFOR'  AND (Date < '03/20/2018') AND (Date >= '09/20/2017') AND [Mnemonic] in
				('AIR FRANCE - KLM',
						'Alcatel Lucent',
						'ALTICE FINCO SA',
						'Altice Luxembourg SA',
						'ArcelorMittal',
						'ARDAGH PACKAGING FIN PUB LTD CO',
						'ASTALDI S per Azioni',
						'Bca Monte dei Paschi di Siena S p A',
						'Bco BPM S per Azioni',
						'Bco Comercial Portugues SA',
						'Boparan Fin PLC',
						'CABLE WIRELESS LTD',
						'CAIXA GERAL DE DEPOSITOS SA',
						'CARE UK HEALTH SOCIAL CARE PLC',
						'CASINO GUICHARDPERRACHON',
						'CERVED GROUP SPA',
						'CMA CGM S A',
						'Constellium NV',
						'Dry Mix Solutions Investissements',
						'Fiat Chrysler Automobiles NV',
						'Financiere Quick',
						'FRONERI INTL LTD',
						'Galapagos Hldg SA',
						'Garfunkelux Holdco 2 SA',
						'GKN LTD',
						'HapagLloyd AG',
						'HEATHROW FDG LTD',
						'Hellenic Telecom Org SA',
						'HEMA BondCo I BV',
						'Iceland Bondco PLC',
						'INEOS Group Hldgs SA',
						'Intl Game Tech PLC',
						'Intrum AB',
						'J Sainsbury PLC',
						'JAGUAR LD ROVER AUTOMOTIVE PLC',
						'LADBROKES CORAL GROUP LTD',
						'Leonardo S per azioni',
						'Louis Dreyfus Co BV',
						'LOXAM',
						'MATALAN FIN PLC',
						'Matterhorn Telecom Hldg SA',
						'Metsa Brd Corp',
						'Monitchem Holdco 3 SA',
						'NEW LOOK SR ISSUER PLC',
						'Nokia Oyj',
						'NOVAFIVES',
						'NXP B.V.',
						'Peugeot SA',
						'Pizzaexpress Fing 1 PLC',
						'Premier Foods Fin PLC',
						'Pub Pwr Corp SA',
						'Rallye',
						'REXEL',
						'Saipem Fin Intl BV',
						'Selecta Group BV',
						--'SFR Group SA',
						'SMURFIT KAPPA ACQUISITIONS',
						'Smurfit Kappa Fdg plc',
						'Stena Aktiebolag',
						'Stonegate Pub Co Fing PLC',
						'Stora Enso CORP',
						'Sunrise Comms Hldgs SA',
						'Syngenta AG',
						'SYNLAB UNSECURED BONDCO',
						'TDC A/S',
						'Techem GmbH',
						'Telecom Italia SpA',
						'TelefonAB L M Ericsson',
						'Tesco PLC',
						'THOMAS COOK GROUP PLC',
						'thyssenkrupp AG',
						'Trionista HoldCo GmbH',
						'TUI AG',
						'TVN Fin Corp III AB publ',
						'Unilabs SubHolding AB publ',
						'Unitymedia Gmb',
						'UPC Hldg BV',
						'VIRGIN MEDIA Fin PLC',
						'VUE INTL BIDCO PLC',
						'Wind Tre SpA',
						'Ziggo Bd Co BV',
						-- Added on July 5th
						'CROWN EUROPEAN HOLDINGS',
						'FCC AQUALIA, S.A.',
						'OI European Group B.V.',
						'United Group B.V.'
						)


			"""

			cds_individual_portfolio = CDS()
			cds_individual_portfolio.connect_db(sql_CDS)
			cds_individual_portfolio.cds_data_transform(100)	
			df_clean = cds_individual_portfolio.df	

	elif cds_input == 0:
		df_clean = pd.DataFrame()
		print('Index...')

	print('Choose which data to input for Index data: ')
	print('1. CDXNAIG: ')
	print('2. 4 major CDS indices (NA, EU): ')
	print('3. NA 2 indices (2006-2009): ')
	print('4. EU 2 indices (2006-2009): ')
	print('5. NA 2 indices (2004-2006): ')
	print('6. EU 2 indices (2004-2006): ')
	print('7. NA 2 indices (2010-2011): ')
	print('8. EU 2 indices (2010-2014): ')
	print('0.: Exit')
	
	while True:
		    index_input = input('Enter your choice: ')
		    try:
		       index_input = int(index_input)
		    except ValueError:
		       print ('Valid number, please')
		       continue
		    if 0 <= index_input <= 8:
		       break
		    else:
		       print ('Valid range, please ')	

	if index_input == 1:
			sql_CDXNAIG_5Y = """
				SELECT [Date]
				      ,[Name] as Ticker
				      ,[Spread] AS Spread5y
				  FROM [hobbit].[dbo].[CDX_index_otr] WHERE (Name = 'CDXNAIG' AND Term = '5Y')
				  ORDER BY Date
			"""
			
			CDXNAIG_5Y = CDS()
			CDXNAIG_5Y.connect_db(sql_CDXNAIG_5Y)
			CDXNAIG_5Y.cds_data_transform()
			df_cdx= CDXNAIG_5Y.df

	if index_input == 2:
			sql_CDX = """
				SELECT [Date]
				      ,[Name] as Ticker
				      ,[Spread] AS Spread5y
				  FROM [hobbit].[dbo].[CDX_index_otr] WHERE Name in ('CDXNAHY', 'CDXNAIG') AND Term = '5Y'
				  ORDER BY Date
			"""
			
			CDXNAIG_5Y = CDS()
			CDXNAIG_5Y.connect_db(sql_CDX)
			CDXNAIG_5Y.cds_data_transform(1500)
			df_cdx= CDXNAIG_5Y.df

			sql_ITRAXX = """
				SELECT [Date]
				      ,[Name] as Ticker
				      ,[Spread] AS Spread5y
				  FROM [hobbit].[dbo].[iTraxx_index_otr] WHERE Name in ('iTraxx Eur', 'iTraxx Eur Xover') AND Term = '5Y'
				  ORDER BY Date
			"""
			
			ITRAXX = CDS()
			ITRAXX.connect_db(sql_ITRAXX)
			ITRAXX.cds_data_transform(500)
			df_itraxx= ITRAXX.df

			df_concat = df_cdx[df_itraxx.index.min():df_itraxx.index.max()]

			df_concat = pd.concat([df_concat, df_itraxx], axis=1)

			df_cdx = df_concat

	if index_input == 3:
			sql_CDXNAIG_5Y = """
					SELECT [Date]
					      ,[Name] as Ticker
					      ,[Spread] AS Spread5y
					  FROM [hobbit].[dbo].[CDX_index_otr] WHERE Name in ('CDXNAHY', 'CDXNAIG') AND Term = '5Y' AND (Date >= '01/01/2006') AND (Date < '01/01/2010')
					  ORDER BY Date
			"""
			
			CDXNAIG_5Y = CDS()
			CDXNAIG_5Y.connect_db(sql_CDXNAIG_5Y)
			CDXNAIG_5Y.cds_data_transform(600)
			df_cdx= CDXNAIG_5Y.df

	if index_input == 4:
			sql_CDXNAIG_5Y = """
				SELECT [Date]
				      ,[Name] as Ticker
				      ,[Spread] AS Spread5y
				  FROM [hobbit].[dbo].[iTraxx_index_otr] WHERE Name in ('iTraxx Eur', 'iTraxx Eur Xover') AND Term = '5Y' AND (Date >= '01/01/2006') AND (Date < '01/01/2010')
				  ORDER BY Date
			"""
			
			CDXNAIG_5Y = CDS()
			CDXNAIG_5Y.connect_db(sql_CDXNAIG_5Y)
			CDXNAIG_5Y.cds_data_transform(600)
			df_cdx= CDXNAIG_5Y.df

	if index_input == 5:
			sql_CDXNAIG_5Y = """
					SELECT [Date]
					      ,[Name] as Ticker
					      ,[Spread] AS Spread5y
					  FROM [hobbit].[dbo].[CDX_index_otr] WHERE Name in ('CDXNAHY', 'CDXNAIG') AND Term = '5Y' AND (Date < '01/01/2006') AND (Date >= '09/20/2004')
					  ORDER BY Date
			"""
			
			CDXNAIG_5Y = CDS()
			CDXNAIG_5Y.connect_db(sql_CDXNAIG_5Y)
			CDXNAIG_5Y.cds_data_transform(200)
			df_cdx= CDXNAIG_5Y.df

	if index_input == 6:
			sql_CDXNAIG_5Y = """
				SELECT [Date]
				      ,[Name] as Ticker
				      ,[Spread] AS Spread5y
				  FROM [hobbit].[dbo].[iTraxx_index_otr] WHERE Name in ('iTraxx Eur', 'iTraxx Eur Xover') AND Term = '5Y' AND (Date < '01/01/2006') AND (Date >= '09/20/2004')
				  ORDER BY Date
			"""
			
			CDXNAIG_5Y = CDS()
			CDXNAIG_5Y.connect_db(sql_CDXNAIG_5Y)
			CDXNAIG_5Y.cds_data_transform(200)
			df_cdx= CDXNAIG_5Y.df

	if index_input == 7:
			sql_CDXNAIG_5Y = """
					SELECT [Date]
					      ,[Name] as Ticker
					      ,[Spread] AS Spread5y
					  FROM [hobbit].[dbo].[CDX_index_otr] WHERE Name in ('CDXNAHY', 'CDXNAIG') AND Term = '5Y' AND (Date < '03/01/2011') AND (Date >= '09/01/2010')
					  ORDER BY Date
			"""
			
			CDXNAIG_5Y = CDS()
			CDXNAIG_5Y.connect_db(sql_CDXNAIG_5Y)
			CDXNAIG_5Y.cds_data_transform(900)
			df_cdx= CDXNAIG_5Y.df

	if index_input == 8:
			sql_CDXNAIG_5Y = """
				SELECT [Date]
				      ,[Name] as Ticker
				      ,[Spread] AS Spread5y
				  FROM [hobbit].[dbo].[iTraxx_index_otr] WHERE Name in ('iTraxx Eur', 'iTraxx Eur Xover') AND Term = '5Y' AND (Date < '09/20/2014') AND (Date >= '01/01/2010')
				  ORDER BY Date
			"""
			
			CDXNAIG_5Y = CDS()
			CDXNAIG_5Y.connect_db(sql_CDXNAIG_5Y)
			CDXNAIG_5Y.cds_data_transform(900)
			df_cdx= CDXNAIG_5Y.df


	elif index_input == 0:
		df_cdx = pd.DataFrame()
		print('PCA...')

	print('Choose from the below options: ')
	print('1. Run PCA on all CDS data along with CDX index: ')
	print('2. Run numpy PCA to determine number of CDS needed for a CDS portfolio: ')
	print('0. Exit')

	while True:
		    choice = input('Enter your choice: ')
		    try:
		       choice = int(choice)
		    except ValueError:
		       print ('Valid number, please')
		       continue
		    if 0 <= choice <= 3:
		       break
		    else:
		       print ('Valid range, please: 1-3')

	return choice, df_clean, df_cdx



# Running the class
if __name__ == "__main__":

	choice, df_clean, df_cdx = main_menu()

	if choice == 1:

		scale = lambda x: (x - x.mean()) / x.std()

		df_concat = df_clean[df_cdx.index.min():df_cdx.index.max()]

		df_concat = pd.concat([df_concat, df_cdx], axis=1)
		df_concat.fillna(method='ffill', inplace = True)
		df_concat.fillna(method='bfill', inplace = True)

		#df_concat = scale(df_concat)

		df_clean = df_concat.iloc[:,:-1]
		df_cdx = df_concat.iloc[:,-1]

		returns = df_clean.pct_change().dropna()

		pca = PCA(n_components=None)
		X_train_pca = pca.fit_transform(returns.cov())

		dates = list(returns.index)

		plt.figure(figsize = (17, 5))
		plt.subplot(121)
		plt.bar(np.arange(len(pca.explained_variance_ratio_[:10])) + .5, pca.explained_variance_ratio_[:10].cumsum())
		plt.ylim((0, 1))
		plt.xlabel('No. of principal components')
		plt.ylabel('Cumulative variance explained')
		plt.grid(axis = 'y', ls = '-', lw = 1, color = 'white')

		plt.subplot(122)
		plt.plot(dates, scale(pca.transform(returns)[:,0]), label = 'PCA Spreads')
		plt.plot(dates, scale(df_cdx.pct_change().dropna()), label = 'CDXNAIG')
		plt.legend(loc = 'upper left')
		plt.ylim(-5,5)
		plt.xlim([datetime.date(2008, 1, 1), datetime.date(2008, 4, 1)])
		plt.show()
		
	elif choice ==2:

		scale = lambda x: (x - x.mean()) / x.std()

		# Concatenating the individual df with the index one.
		# Comment out if not needed.
		#df_concat = df_clean[df_cdx.index.min():df_cdx.index.max()]
		#df_concat = pd.concat([df_concat, df_cdx], axis=1)
		#df_concat.fillna(method='ffill', inplace = True)
		#df_concat.fillna(method='bfill', inplace = True)
		#df_clean = df_concat#.iloc[:,:-1]
		#df_cdx = df_concat.iloc[:,-1]

		deletion_crit = 1
		stopping_criteria = 1
		go_to_next_round = True

		sc = StandardScaler()
		round_1 = df_clean

		X_train_std = sc.fit_transform(round_1)

		cov_mat = np.corrcoef(X_train_std.T)
		eigen_vals, eigen_vecs = np.linalg.eig(cov_mat)
		print('\nEigenvalues \n%s' % eigen_vals)
		print('\nEigenvectors \n%s' % eigen_vecs)

		# Print out corr matrix
		corr_mat_for_MST = cov_mat
		#df_out = pd.DataFrame(data=cov_mat,index=df_clean.columns,columns=df_clean.columns)
		#df_out.to_csv('out.csv')

		# Record the eigen values greater than 1
		boolarr = (eigen_vals >= deletion_crit)
		PC_to_use = np.sum(boolarr)

		round = 1
		set_unique_CDS_to_delete = set([])

		for ind in range(len(boolarr)):
			if boolarr[ind] == False:
				#w = eigen_vecs[:,ind]
				#X_train_pca = X_train_std.dot(w)
				set_unique_CDS_to_delete.add(np.argmax(abs(eigen_vecs[:,ind])))


		#Export round to excel
		# Create a Pandas Excel writer using XlsxWriter as the engine.
		writer = pd.ExcelWriter('round_output.xlsx', engine='xlsxwriter')

		df_to_print = pd.DataFrame(data= np.atleast_2d(eigen_vals)).append(pd.DataFrame(data=eigen_vecs,index=round_1.columns))
		df_to_print.to_excel(writer, sheet_name='Round {}, {}_CDSs'.format(round, len(boolarr)), index=True)

		if np.min(eigen_vals) > stopping_criteria:
			go_to_next_round = False

		if go_to_next_round == True:
			round_2 = round_1.drop(round_1.columns[(list(set_unique_CDS_to_delete))],axis=1)		

			round += 1
			

			#cds_individual_portfolio.plot_variance(eigen_vals)

			X_train_std = sc.fit_transform(round_2)

			cov_mat = np.corrcoef(X_train_std.T)
			eigen_vals, eigen_vecs = np.linalg.eig(cov_mat)
			print('\nEigenvalues \n%s' % eigen_vals)
			print('\nEigenvectors \n%s' % eigen_vecs)

			# Record the eigen values greater than 1
			boolarr = (eigen_vals >= deletion_crit)
			PC_to_use = np.sum(boolarr)

			set_unique_CDS_to_delete = set([])

			for ind in range(len(boolarr)):
				if boolarr[ind] == False:
					#w = eigen_vecs[:,ind]
					#X_train_pca = X_train_std.dot(w)
					set_unique_CDS_to_delete.add(np.argmax(abs(eigen_vecs[:,ind])))

			df_to_print = pd.DataFrame(data= np.atleast_2d(eigen_vals)).append(pd.DataFrame(data=eigen_vecs,index=round_2.columns))
			df_to_print.to_excel(writer, sheet_name='Round {}, {}_CDSs'.format(round, len(boolarr)), index=True)

		if np.min(eigen_vals) > stopping_criteria:
			go_to_next_round = False

		if go_to_next_round == True:

			round_3 = round_2.drop(round_2.columns[(list(set_unique_CDS_to_delete))],axis=1)


			round += 1

			X_train_std = sc.fit_transform(round_3)

			cov_mat = np.corrcoef(X_train_std.T)
			eigen_vals, eigen_vecs = np.linalg.eig(cov_mat)
			print('\nEigenvalues \n%s' % eigen_vals)
			print('\nEigenvectors \n%s' % eigen_vecs)

			# Record the eigen values greater than 1
			boolarr = (eigen_vals >= deletion_crit)
			PC_to_use = np.sum(boolarr)

			set_unique_CDS_to_delete = set([])

			for ind in range(len(boolarr)):
				if boolarr[ind] == False:
					#w = eigen_vecs[:,ind]
					#X_train_pca = X_train_std.dot(w)
					set_unique_CDS_to_delete.add(np.argmax(abs(eigen_vecs[:,ind])))

			df_to_print = pd.DataFrame(data= np.atleast_2d(eigen_vals)).append(pd.DataFrame(data=eigen_vecs,index=round_3.columns))
			df_to_print.to_excel(writer, sheet_name='Round {}, {}_CDSs'.format(round, len(boolarr)), index=True)

		if np.min(eigen_vals) > stopping_criteria:
			go_to_next_round = False

		if go_to_next_round == True:


			round_4 = round_3.drop(round_3.columns[(list(set_unique_CDS_to_delete))],axis=1)


			round += 1

			X_train_std = sc.fit_transform(round_4)

			cov_mat = np.corrcoef(X_train_std.T)
			eigen_vals, eigen_vecs = np.linalg.eig(cov_mat)
			print('\nEigenvalues \n%s' % eigen_vals)
			print('\nEigenvectors \n%s' % eigen_vecs)

			# Record the eigen values greater than 1
			boolarr = (eigen_vals >= deletion_crit)
			PC_to_use = np.sum(boolarr)

			set_unique_CDS_to_delete = set([])

			for ind in range(len(boolarr)):
				if boolarr[ind] == False:
					#w = eigen_vecs[:,ind]
					#X_train_pca = X_train_std.dot(w)
					set_unique_CDS_to_delete.add(np.argmax(abs(eigen_vecs[:,ind])))


			df_to_print = pd.DataFrame(data= np.atleast_2d(eigen_vals)).append(pd.DataFrame(data=eigen_vecs,index=round_4.columns))
			df_to_print.to_excel(writer, sheet_name='Round {}, {}_CDSs'.format(round, len(boolarr)), index=True)

		if np.min(eigen_vals) > stopping_criteria:
			go_to_next_round = False

		if go_to_next_round == True:


			round_5 = round_4.drop(round_4.columns[(list(set_unique_CDS_to_delete))],axis=1)

			round += 1

			X_train_std = sc.fit_transform(round_5)

			cov_mat = np.corrcoef(X_train_std.T)
			eigen_vals, eigen_vecs = np.linalg.eig(cov_mat)
			print('\nEigenvalues \n%s' % eigen_vals)
			print('\nEigenvectors \n%s' % eigen_vecs)

			# Record the eigen values greater than 1
			boolarr = (eigen_vals >= deletion_crit)
			PC_to_use = np.sum(boolarr)

			set_unique_CDS_to_delete = set([])

			for ind in range(len(boolarr)):
				if boolarr[ind] == False:
					#w = eigen_vecs[:,ind]
					#X_train_pca = X_train_std.dot(w)
					set_unique_CDS_to_delete.add(np.argmax(abs(eigen_vecs[:,ind])))


			df_to_print = pd.DataFrame(data= np.atleast_2d(eigen_vals)).append(pd.DataFrame(data=eigen_vecs,index=round_5.columns))
			df_to_print.to_excel(writer, sheet_name='Round {}, {}_CDSs'.format(round, len(boolarr)), index=True)

		if np.min(eigen_vals) > stopping_criteria:
			go_to_next_round = False

		if go_to_next_round == True:

			round_6 = round_5.drop(round_5.columns[(list(set_unique_CDS_to_delete))],axis=1)

			round += 1

			X_train_std = sc.fit_transform(round_6)

			cov_mat = np.corrcoef(X_train_std.T)
			eigen_vals, eigen_vecs = np.linalg.eig(cov_mat)
			print('\nEigenvalues \n%s' % eigen_vals)
			print('\nEigenvectors \n%s' % eigen_vecs)

			# Record the eigen values greater than 1
			boolarr = (eigen_vals >= deletion_crit)
			PC_to_use = np.sum(boolarr)

			set_unique_CDS_to_delete = set([])

			for ind in range(len(boolarr)):
				if boolarr[ind] == False:
					#w = eigen_vecs[:,ind]
					#X_train_pca = X_train_std.dot(w)
					set_unique_CDS_to_delete.add(np.argmax(abs(eigen_vecs[:,ind])))


			df_to_print = pd.DataFrame(data= np.atleast_2d(eigen_vals)).append(pd.DataFrame(data=eigen_vecs,index=round_6.columns))
			df_to_print.to_excel(writer, sheet_name='Round {}, {}_CDSs'.format(round, len(boolarr)), index=True)

		if np.min(eigen_vals) > stopping_criteria:
			go_to_next_round = False

		if go_to_next_round == True:


			round_7 = round_6.drop(round_6.columns[(list(set_unique_CDS_to_delete))],axis=1)

			round += 1

			X_train_std = sc.fit_transform(round_7)

			cov_mat = np.corrcoef(X_train_std.T)
			eigen_vals, eigen_vecs = np.linalg.eig(cov_mat)
			print('\nEigenvalues \n%s' % eigen_vals)
			print('\nEigenvectors \n%s' % eigen_vecs)

			# Record the eigen values greater than 1
			boolarr = (eigen_vals >= deletion_crit)
			PC_to_use = np.sum(boolarr)

			set_unique_CDS_to_delete = set([])

			for ind in range(len(boolarr)):
				if boolarr[ind] == False:
					#w = eigen_vecs[:,ind]
					#X_train_pca = X_train_std.dot(w)
					set_unique_CDS_to_delete.add(np.argmax(abs(eigen_vecs[:,ind])))

			df_to_print = pd.DataFrame(data= np.atleast_2d(eigen_vals)).append(pd.DataFrame(data=eigen_vecs,index=round_7.columns))
			df_to_print.to_excel(writer, sheet_name='Round {}, {}_CDSs'.format(round, len(boolarr)), index=True)

		if np.min(eigen_vals) > stopping_criteria:
			go_to_next_round = False

		if go_to_next_round == True:

			round_8 = round_7.drop(round_7.columns[(list(set_unique_CDS_to_delete))],axis=1)

			round += 1

			X_train_std = sc.fit_transform(round_8)

			cov_mat = np.corrcoef(X_train_std.T)
			eigen_vals, eigen_vecs = np.linalg.eig(cov_mat)
			print('\nEigenvalues \n%s' % eigen_vals)
			print('\nEigenvectors \n%s' % eigen_vecs)

			# Record the eigen values greater than 1
			boolarr = (eigen_vals >= deletion_crit)
			PC_to_use = np.sum(boolarr)

			set_unique_CDS_to_delete = set([])

			for ind in range(len(boolarr)):
				if boolarr[ind] == False:
					#w = eigen_vecs[:,ind]
					#X_train_pca = X_train_std.dot(w)
					set_unique_CDS_to_delete.add(np.argmax(abs(eigen_vecs[:,ind])))

			df_to_print = pd.DataFrame(data= np.atleast_2d(eigen_vals)).append(pd.DataFrame(data=eigen_vecs,index=round_8.columns))
			df_to_print.to_excel(writer, sheet_name='Round {}, {}_CDSs'.format(round, len(boolarr)), index=True)

		if np.min(eigen_vals) > stopping_criteria:
			go_to_next_round = False

		if go_to_next_round == True:

			round_9 = round_8.drop(round_8.columns[(list(set_unique_CDS_to_delete))],axis=1)

			round += 1

			X_train_std = sc.fit_transform(round_9)

			cov_mat = np.corrcoef(X_train_std.T)
			eigen_vals, eigen_vecs = np.linalg.eig(cov_mat)
			print('\nEigenvalues \n%s' % eigen_vals)
			print('\nEigenvectors \n%s' % eigen_vecs)

			# Record the eigen values greater than 1
			boolarr = (eigen_vals >= deletion_crit)
			PC_to_use = np.sum(boolarr)

			set_unique_CDS_to_delete = set([])

			for ind in range(len(boolarr)):
				if boolarr[ind] == False:
					#w = eigen_vecs[:,ind]
					#X_train_pca = X_train_std.dot(w)
					set_unique_CDS_to_delete.add(np.argmax(abs(eigen_vecs[:,ind])))

			df_to_print = pd.DataFrame(data= np.atleast_2d(eigen_vals)).append(pd.DataFrame(data=eigen_vecs,index=round_9.columns))
			df_to_print.to_excel(writer, sheet_name='Round {}, {}_CDSs'.format(round, len(boolarr)), index=True)

		if np.min(eigen_vals) > stopping_criteria:
			go_to_next_round = False

		if go_to_next_round == True:

			round_10 = round_9.drop(round_9.columns[(list(set_unique_CDS_to_delete))],axis=1)

			round += 1

			X_train_std = sc.fit_transform(round_10)

			cov_mat = np.corrcoef(X_train_std.T)
			eigen_vals, eigen_vecs = np.linalg.eig(cov_mat)
			print('\nEigenvalues \n%s' % eigen_vals)
			print('\nEigenvectors \n%s' % eigen_vecs)

			# Record the eigen values greater than 1
			boolarr = (eigen_vals >= deletion_crit)
			PC_to_use = np.sum(boolarr)

			set_unique_CDS_to_delete = set([])

			for ind in range(len(boolarr)):
				if boolarr[ind] == False:
					#w = eigen_vecs[:,ind]
					#X_train_pca = X_train_std.dot(w)
					set_unique_CDS_to_delete.add(np.argmax(abs(eigen_vecs[:,ind])))


			df_to_print = pd.DataFrame(data= np.atleast_2d(eigen_vals)).append(pd.DataFrame(data=eigen_vecs,index=round_10.columns))
			df_to_print.to_excel(writer, sheet_name='Round {}, {}_CDSs'.format(round, len(boolarr)), index=True)

		if np.min(eigen_vals) > stopping_criteria:
			go_to_next_round = False

		if go_to_next_round == True:

			round_11 = round_10.drop(round_10.columns[(list(set_unique_CDS_to_delete))],axis=1)

			round += 1

			X_train_std = sc.fit_transform(round_11)

			cov_mat = np.corrcoef(X_train_std.T)
			eigen_vals, eigen_vecs = np.linalg.eig(cov_mat)
			print('\nEigenvalues \n%s' % eigen_vals)
			print('\nEigenvectors \n%s' % eigen_vecs)

			# Record the eigen values greater than 1
			boolarr = (eigen_vals >= deletion_crit)
			PC_to_use = np.sum(boolarr)

			set_unique_CDS_to_delete = set([])

			for ind in range(len(boolarr)):
				if boolarr[ind] == False:
					#w = eigen_vecs[:,ind]
					#X_train_pca = X_train_std.dot(w)
					set_unique_CDS_to_delete.add(np.argmax(abs(eigen_vecs[:,ind])))


			df_to_print = pd.DataFrame(data= np.atleast_2d(eigen_vals)).append(pd.DataFrame(data=eigen_vecs,index=round_11.columns))
			df_to_print.to_excel(writer, sheet_name='Round {}, {}_CDSs'.format(round, len(boolarr)), index=True)

		if np.min(eigen_vals) > stopping_criteria:
			go_to_next_round = False

		if go_to_next_round == True:

			round_12 = round_11.drop(round_11.columns[(list(set_unique_CDS_to_delete))],axis=1)

			round += 1

			X_train_std = sc.fit_transform(round_12)

			cov_mat = np.corrcoef(X_train_std.T)
			eigen_vals, eigen_vecs = np.linalg.eig(cov_mat)
			print('\nEigenvalues \n%s' % eigen_vals)
			print('\nEigenvectors \n%s' % eigen_vecs)

			# Record the eigen values greater than 1
			boolarr = (eigen_vals >= deletion_crit)
			PC_to_use = np.sum(boolarr)

			set_unique_CDS_to_delete = set([])

			for ind in range(len(boolarr)):
				if boolarr[ind] == False:
					#w = eigen_vecs[:,ind]
					#X_train_pca = X_train_std.dot(w)
					set_unique_CDS_to_delete.add(np.argmax(abs(eigen_vecs[:,ind])))


			df_to_print = pd.DataFrame(data= np.atleast_2d(eigen_vals)).append(pd.DataFrame(data=eigen_vecs,index=round_12.columns))
			df_to_print.to_excel(writer, sheet_name='Round {}, {}_CDSs'.format(round, len(boolarr)), index=True)

			round_13 = round_12.drop(round_12.columns[(list(set_unique_CDS_to_delete))],axis=1)

		writer.save()


	elif choice == 3:

		# Without transposing the matrix
		sc = StandardScaler()

		round_1 = df_clean
		
		X_train_std = sc.fit_transform(round_1)
		cov_mat = np.cov(X_train_std.T)
		eigen_vals, eigen_vecs = np.linalg.eig(cov_mat)
		print('\nEigenvalues \n%s' % eigen_vals)
		print('\nEigenvectors \n%s' % eigen_vecs)
		
		# Record the eigen values greater than 1
		boolarr = (eigen_vals >= 1)
		PC_to_use = np.sum(boolarr)
		set_unique_CDS_to_delete = set([])



	elif choice == 0:
		print('Exiting...')
		

