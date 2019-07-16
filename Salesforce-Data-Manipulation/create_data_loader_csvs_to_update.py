# Create data loader file to update/insert new records into implemented product data 
import pandas as pd
import datetime
import glob
import zipfile
from os.path import basename
import os

def set_trace():
	from IPython.core.debugger import Pdb
	import sys
	Pdb(color_scheme='Linux').set_trace(sys._getframe().f_back)

################### STATIC DATA ########################################################
# Import version mapping
version_map = pd.read_excel("../Implemented Products/static_data_new.xlsx", sheetname = 1)

# Create base df for the uploader file
# This will be filled up with data from the other spreadsheets
columns = ['Id','Account__c', 'Asset_Class__c', 'Implemation_Status__c', 
           'Module__c', 'Product_Version__c', 'Reference__c', 
           'Solution__c', 'SubSolution__c']

base_loader_csv = pd.DataFrame(columns=columns)


################## PROCESSING SPREADSHEETS #############################################

# Iterating through all the spredsheets in the folder.
path = '../Implemented Products/Completed spreadsheets/*.xlsx'

# List to store filenames.
file_name_list = list()

for fname in glob.glob(path):
	print(fname)
	file_name_list = file_name_list + [fname]

	df = pd.read_excel(fname, sheetname = 0)
	id_df = pd.read_excel(fname, sheetname = 1)

	# Getting acc ID.
	#acc_name = df.columns[0]
	acc_id = df.columns[0]


	df.drop(acc_id, axis=1, inplace=True)
	id_df.drop(acc_id, axis=1, inplace=True)

	# Split df into modules/ifs/Packages

	######## Process Modules ########
	modules_df = df[df['Drawloop_Product_Family_Formula'] == 'Module']
	modules_id_df = id_df[id_df['Drawloop_Product_Family_Formula'] == 'Module']

	for col in range(2,len(modules_df.columns)):
	 	for mod_row in range(0,len(modules_df)):
	 		# Create rows only for items where we have somethign.
	 		

	 		if pd.notnull(modules_df.iloc[mod_row,col]):
	 			  # print('Col#: ', col)
	 		      # print('Row#: ', mod_row)

	 			  #set_trace()

	 			  if (modules_id_df.shape[0]> mod_row) and (modules_id_df.shape[1]> col):
	 			  	upsert_id = modules_id_df.iloc[mod_row,col]
	 			  else:
	 			  	upsert_id = ''

	 			  # String value to work with
	 			  value_string = modules_df.iloc[mod_row,col]

	 			  # Getting assett class which is the column name
	 			  asset_class = modules_df.columns[col]

	 			  # Getting implementation status
	 			  impl = value_string.split('-')[0]
	 			  if impl == 'LIVE':
	 			  	impl = 'Live'
	 			  elif impl == 'IMPL':
	 			  	impl = 'In Implementation'
	 			  else:
	 			  	impl = 'In Implementation'

				  # Getting version
	 			  version = value_string.split('-')[1]
	 			  version = version_map[version_map['Name to match'] == version].iloc[0,2]

	 			  # Getting referencability
	 			  
	 			  if len(value_string.split('-')) == 3:
		 			  referencable = value_string.split('-')[2]
		 			  if referencable == 'R':
		 			  	referencable = 'Yes'
		 			  else:
		 			  	referencable = 'No'
		 		  else:
		 		  	  referencable = float('NaN')




	 			  base_loader_csv = base_loader_csv.append(pd.DataFrame([[upsert_id,acc_id,asset_class,
	 			  	impl,modules_df.iloc[mod_row,0],
	 			  	version,referencable,float('NaN'),float('NaN')]], columns=columns))

	# modules_df.iloc[mod_row,0]

	######## Process Packages ########
	package_df = df[df['Drawloop_Product_Family_Formula'] == 'Package']
	package_id_df = id_df[id_df['Drawloop_Product_Family_Formula'] == 'Package']

	for col in range(2,len(package_df.columns)):
	 	for mod_row in range(0,len(package_df)):
	 		# Create rows only for items where we have somethign.
	 		

	 		if pd.notnull(package_df.iloc[mod_row,col]):
				# print('Col#: ', col)
	 		    # print('Row#: ', mod_row)

	 		    if (package_id_df.shape[0]> mod_row) and (package_id_df.shape[1]> col):
	 		    	upsert_id = package_id_df.iloc[mod_row,col]
	 		    else:
	 		      	upsert_id = ''

				# String value to work with
	 		    value_string = package_df.iloc[mod_row,col]
				
	 			# Getting assett class which is the column name
	 		    asset_class = package_df.columns[col]

	 			# Getting implementation status
	 		    impl = value_string.split('-')[0]
	 		    if impl == 'LIVE':
	 		    	impl = 'Live'
	 		    elif impl == 'IMPL':
	 		     	impl = 'In Implementation'
	 		    else:
	 		      	impl = 'In Implementation'

				# Getting version
	 		    version = value_string.split('-')[1]
	 		    version = version_map[version_map['Name to match'] == version].iloc[0,2]

	 			# Getting referencability
	 		    if len(value_string.split('-')) == 3:
	 		    	referencable = value_string.split('-')[2]
	 		    	if referencable == 'R':
		 		      	referencable = 'Yes'
	 		    	else:
		 		      	referencable = 'No'
	 		    else:
	 		    	referencable = float('NaN')


	 		    base_loader_csv = base_loader_csv.append(pd.DataFrame([[upsert_id,acc_id,asset_class,
	 			  	impl,package_df.iloc[mod_row,0],
	 			  	version,referencable,float('NaN'),float('NaN')]], columns=columns))



	####### Process Interfaces #################
	interfaces_df = df[df['Drawloop_Product_Family_Formula'] == 'Interface']
	interfaces_id_df = id_df[id_df['Drawloop_Product_Family_Formula'] == 'Interface']


	for mod_row in range(0,len(interfaces_df)):
	 		# Create rows only for items where we have somethign.
	 		

	 		if pd.notnull(interfaces_df.iloc[mod_row,2]):
	 			  # print('Col#: ', col)
	 		      # print('Row#: ', mod_row)

	 		      if (interfaces_id_df.shape[0]> mod_row) and (interfaces_id_df.shape[1]> col):
	 		      	upsert_id = interfaces_id_df.iloc[mod_row,2]
	 		      else:
	 		      	upsert_id = ''

	 			  # String value to work with
	 		      value_string = interfaces_df.iloc[mod_row,2]

	 			  # Getting assett class which is the column name
	 		      asset_class = float('NaN')

	 			  # Getting implementation status
	 		      impl = value_string.split('-')[0]
	 		      if impl == 'LIVE':
	 		      	impl = 'Live'
	 		      elif impl == 'IMPL':
	 		      	impl = 'In Implementation'
	 		      else:
	 		      	impl = 'In Implementation'

				  # Getting version
	 		      version = value_string.split('-')[1]
	 		      version = version_map[version_map['Name to match'] == version].iloc[0,2]

	 			  # Getting referencability
	 		      if len(value_string.split('-')) == 3:
	 		      	  referencable = value_string.split('-')[2]
	 		      	  if referencable == 'R':
	 		      	  	referencable = 'Yes'
	 		      	  else:
	 		      	  	referencable = 'No'
	 		      else:
	 		        	  referencable = float('NaN')


	 		      base_loader_csv = base_loader_csv.append(pd.DataFrame([[upsert_id,acc_id,asset_class,
	 			  	impl,interfaces_df.iloc[mod_row,0],
	 			  	version,referencable,float('NaN'),float('NaN')]], columns=columns))

# Write out the uploader file into csv.
base_loader_csv.to_csv("../Implemented Products/Completed spreadsheets/Generated uploader files/import_impl_prod_{}.csv".format(datetime.date.today().strftime("%m%d%Y")),index=False)

# Zip up xlsx files
with zipfile.ZipFile('../Implemented Products/Completed spreadsheets/zippedInputExcels_' + datetime.date.today().strftime("%m%d%Y") + '.zip', 'w') as myzip:
    for f in file_name_list:
	    # Note: zip wrote requires the full path, and the file name wihtouht the path (if the file is not in current dir)
	    myzip.write(f.replace('\\','/'), basename(f.replace('\\','/')))
	    # Remove files zipped.
	    os.remove(f.replace('\\','/'))
myzip.close()