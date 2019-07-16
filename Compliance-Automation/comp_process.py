import pandas as pd
import numpy as np
import datetime
import glob
import pdb

path = '../2016_Compliance_letters/Spreadsheets/*.xlsx'

number_of_users_accessed = 0
number_of_users_accessed_in_group = 0

columns = ['client', 'number_of_users_accessed', 'number_of_users_accessed_in_group']

result_df = pd.DataFrame(columns=columns)

for fname in glob.glob(path):
	print(fname)
	number_of_users_accessed = 0
	number_of_users_accessed_in_group = 0
	df_user_groups = pd.read_excel(fname, sheetname = 0)
	df_user_table = pd.read_excel(fname, sheetname = 1)
	unique_users = df_user_table.iloc[:,0].unique()
	number_of_users_accessed = len(unique_users)
	# Drop users who were locked before 2016 Jan 1
	#pdb.set_trace()
	if (type(df_user_groups.iloc[0,2]) != np.float64):
		df_user_groups = df_user_groups[(df_user_groups.iloc[:,2] >= '1/1/2016') | (df_user_groups.iloc[:,2].isnull() ) ]

	for u in unique_users:
		#print(u)
		if len(df_user_groups[df_user_groups.iloc[:,0]==u] > 0):
			number_of_users_accessed_in_group += 1
		#print (number_of_users_accessed_in_group)

	result_df = result_df.append(pd.DataFrame([[fname, number_of_users_accessed,number_of_users_accessed_in_group]], columns=columns))



result_df.to_excel('../2016_Compliance_letters/compliance_result_{}.xlsx'.format(datetime.date.today().strftime("%m%d%Y")),index=False)