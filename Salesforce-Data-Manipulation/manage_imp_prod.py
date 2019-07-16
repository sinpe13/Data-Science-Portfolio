# This application manages implemented products from the Salesforce data
# It is capable of downloading salesforce reports and generate the implemented products spreadsheet from them.
# Also create upsert uploader files from the updated spreadsheets based on CSM updates in the file. 

import pandas as pd
import numpy as np
import datetime
import salesforce_reporting
from salesforce_reporting import Connection, ReportParser

test = 0

if test == 1:

	impprod_sheet = ImpProdData()
	#purchased_prod_df, implemented_prod_df = impprod_sheet.extract_from_Salesforce()
	purchased_prod_df, implemented_prod_df = impprod_sheet.extract_from_spreadsheet()
	impprod_sheet.process(purchased_prod_df, implemented_prod_df)

	# Sandbox test login
	token = 'test'
	user_id = 'test'
	password = 'test'
	report_id = 'test'



class ImpProdData():
	def __init__(self):
		self.output_df = pd.DataFrame()


	def extract_from_Salesforce(self):
		
		###### EXTRACT PURCHASED PRODUCTS #######

		#user_id = input('Enter your user_id: ')
		#password = input('Enter your password: ')
		#token = input('Enter your token: ')
		#report_id = input('Enter your report_id: ')

		token = 'test'
		user_id = 'test'
		password = 'test'
		report_id = 'test'

		# Address sandbox
		#sandbox = input('Sandbox (y/n): ')
		
		sf = Connection(username=user_id, password=password, security_token=token, sandbox=True)
		report = sf.get_report(report_id, details=True)
		parser = salesforce_reporting.ReportParser(report)
		columns_from_sfdc =  parser._get_field_labels()
		#print(columns_from_sfdc)
		column_order = list(columns_from_sfdc.values())

		df = pd.DataFrame()
		df = df.from_dict(parser.records_dict())
		
		purchased_prod_df = df

		###### EXTRACT IMPLEMENTED PRODUCTS #######

		#user_id = input('Enter your user_id: ')
		#password = input('Enter your password: ')
		#token = input('Enter your token: ')
		#report_id = input('Enter your report_id: ')

		token = 'test'
		user_id = 'test'
		password = 'test'
		report_id = 'test'

		# Address sandbox
		#sandbox = input('Sandbox (y/n): ')
		
		sf = Connection(username=user_id, password=password, security_token=token, sandbox=True)
		report = sf.get_report(report_id, details=True)
		parser = salesforce_reporting.ReportParser(report)
		columns_from_sfdc =  parser._get_field_labels()
		#print(columns_from_sfdc)
		column_order = list(columns_from_sfdc.values())

		df = pd.DataFrame()
		df = df.from_dict(parser.records_dict())
		
		implemented_prod_df = df

		return purchased_prod_df, implemented_prod_df
		#self.df = df[column_order]
		# Further parsing for df needs to be added if extracted from SFDC

	def extract_from_spreadsheet(self):
		# Check if it is path_to_file or self.path
		purchased_prod_df = pd.read_excel('..//Implemented Products/input_files_for_update_impl_prods/purchased_product_data.xlsx', skip_footer=6)
		implemented_prod_df = pd.read_excel('..//Implemented Products/input_files_for_update_impl_prods/implemented_product_data.xlsx', skip_footer=6)

		return purchased_prod_df, implemented_prod_df

	def process(self,purchased_prod_df, implemented_prod_df):

		df = pd.DataFrame()
		df = purchased_prod_df
		df_impl = implemented_prod_df
		account_ids = df.loc[:,'Account Name: Account 18 digit Id'].unique()

		for account in account_ids:
			# bt_df is the temporary DF with the actual clients rows from the big dataframe.

			print('Processing account: ' + account)
			bt_df = df[df['Account Name: Account 18 digit Id'] == account]

			bt_df['Drawloop_Product_Family_Formula'] = pd.Categorical(bt_df['Drawloop_Product_Family_Formula'], ['Asset Class', 'Module', 'Package', 'Interface']) 
			bt_df.sort_values(['Drawloop_Product_Family_Formula','Drawloop_Product_Name_Formula'], inplace=True)

			asset_columns = bt_df['Drawloop_Product_Name_Formula'][bt_df['Drawloop_Product_Family_Formula'] == 'Asset Class']
			asset_columns = asset_columns.tolist()

			result_df = bt_df[['Drawloop_Product_Name_Formula','Drawloop_Product_Family_Formula']][bt_df['Drawloop_Product_Family_Formula'] != 'Asset Class']
			
			for i in asset_columns:
				result_df[i] =  ''

			#result_df.index.name = bt_df['Account Name: Account Name'].iloc[0]


			imp_prod_df = result_df.drop_duplicates().set_index(['Drawloop_Product_Name_Formula', 'Drawloop_Product_Family_Formula'])
			id_df = result_df.drop_duplicates().set_index(['Drawloop_Product_Name_Formula', 'Drawloop_Product_Family_Formula'])

			impl_for_account_df = df_impl[df_impl['Account Name: Account 18 digit Id'] == account]

			for i in range(len(impl_for_account_df)):
				
				if impl_for_account_df['Implementation Status'].iloc[i] == 'Live':
	 				impl = 'LIVE'
				elif impl_for_account_df['Implementation Status'].iloc[i] == 'In Implementation':
	 			  	impl = 'IMPL'
				else:
	 			  	impl = 'IMPL'

				if impl_for_account_df['Reference'].iloc[i] == 'Yes':
		 			  	referencable = 'R'
				else:
		 			  	referencable = 'N'

		 		# If no asset class meaining it`s interface
				if (type(impl_for_account_df['Asset Class'].iloc[i]) == float) & (imp_prod_df.columns.size > 0):
					imp_prod_df.loc[impl_for_account_df['Module'].iloc[i],imp_prod_df.columns[0]] = impl + '-' + impl_for_account_df['Version'].iloc[i] + '-' + referencable
					id_df.loc[impl_for_account_df['Module'].iloc[i],imp_prod_df.columns[0]] = impl_for_account_df['Product Information: ID'].iloc[i]

				# Handle when there is no asset class sold.
				elif (type(impl_for_account_df['Asset Class'].iloc[i]) == float) & (imp_prod_df.columns.size == 0):
					imp_prod_df[''] = ''
					id_df[''] = ''
					imp_prod_df.loc[impl_for_account_df['Module'].iloc[i],imp_prod_df.columns[0]] = impl + '-' + impl_for_account_df['Version'].iloc[i] + '-' + referencable
					id_df.loc[impl_for_account_df['Module'].iloc[i],imp_prod_df.columns[0]] = impl_for_account_df['Product Information: ID'].iloc[i]

				else:
					imp_prod_df.loc[impl_for_account_df['Module'].iloc[i],impl_for_account_df['Asset Class'].iloc[i]] = impl + '-' + impl_for_account_df['Version'].iloc[i] + '-' + referencable
					id_df.loc[impl_for_account_df['Module'].iloc[i],impl_for_account_df['Asset Class'].iloc[i]] = impl_for_account_df['Product Information: ID'].iloc[i]

			imp_prod_df = imp_prod_df.reset_index()
			id_df = id_df.reset_index()
			imp_prod_df.index.name = account
			id_df.index.name = account

			writer = pd.ExcelWriter('..//Implemented Products/output_files_for_update_impl_prods/{}.xlsx'.format(bt_df['Account Name: Account Name'].iloc[0].replace('/', '')), engine='xlsxwriter')

			imp_prod_df.to_excel(writer, sheet_name='imp_prod_matrix', index=True)
			id_df.to_excel(writer, sheet_name='prod_ids', index=True)

			writer.save()