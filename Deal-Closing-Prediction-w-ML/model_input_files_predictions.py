import pandas as pd

#df = pd.read_csv('C:/Final Documents for Research Project/2 Question 2 - Probability of winning opportunity in stage x/5 Model Definitions/Data Stage 2.csv')
df = pd.read_csv('C:/Final Documents for Research Project/2 Question 2 - Probability of winning opportunity in stage x/5 Model Definitions/Data Stage 2-3.csv')
#df = pd.read_csv('C:/Final Documents for Research Project/2 Question 2 - Probability of winning opportunity in stage x/5 Model Definitions/Data Stage 2-4.csv')
#df = pd.read_csv('C:/Final Documents for Research Project/2 Question 2 - Probability of winning opportunity in stage x/5 Model Definitions/Data Stage 2-5.csv')

############################# Functions to use ##################################################

def format_win_column(input_df):
	input_df['Prediction'] = input_df['Stage'].apply(lambda x: 1 if x == 'Win' else -1)
	input_df = input_df.drop(['Stage','Close Quarter','Created Date','Opportunity Owner Manager'],axis=1)
	return input_df

#################### Plotting validation curve ##################################################

print(__doc__)

import matplotlib.pyplot as plt
import numpy as np

from sklearn.svm import SVC
from sklearn.model_selection import validation_curve

def valid_cuve(X, y, model, title):

	param_range = np.logspace(-10, -1, 10)
	train_scores, test_scores = validation_curve(
		   clf_fitted, X, y, param_name="gamma", param_range=param_range,
		   cv=10, scoring="accuracy", n_jobs=1)
	train_scores_mean = np.mean(train_scores, axis=1)
	train_scores_std = np.std(train_scores, axis=1)
	test_scores_mean = np.mean(test_scores, axis=1)
	test_scores_std = np.std(test_scores, axis=1)
	plt.title(title)
	plt.xlabel("$\gamma$")
	plt.ylabel("Score")
	plt.ylim(0.0, 1.1)
	lw = 2
	plt.semilogx(param_range, train_scores_mean, label="Training score",
		            color="darkorange", lw=lw)
	plt.fill_between(param_range, train_scores_mean - train_scores_std,
		                train_scores_mean + train_scores_std, alpha=0.2,
		                color="darkorange", lw=lw)
	plt.semilogx(param_range, test_scores_mean, label="Cross-validation score",
		            color="navy", lw=lw)
	plt.fill_between(param_range, test_scores_mean - test_scores_std,
		                test_scores_mean + test_scores_std, alpha=0.2,
		                color="navy", lw=lw)
	plt.legend(loc="best")
	#plt.show()
	return plt

#################################### Learning curve ####################################################

print(__doc__)

import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.model_selection import learning_curve
from sklearn.model_selection import ShuffleSplit


def learn_curve(X, y, model,title):
	train_sizes, train_scores, test_scores = learning_curve(model, X, y, train_sizes = [150, 462], cv = 3)

	plt.figure()
	plt.xlabel("Training examples")
	plt.ylabel("Score")
	plt.title(title)

	train_scores_mean = np.mean(train_scores, axis=1)
	train_scores_std = np.std(train_scores, axis=1)
	test_scores_mean = np.mean(test_scores, axis=1)
	test_scores_std = np.std(test_scores, axis=1)

	plt.grid()
	plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
	                 train_scores_mean + train_scores_std, alpha=0.1,
	                 color="r")
	plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
	                 test_scores_mean + test_scores_std, alpha=0.1, color="g")
	plt.plot(train_sizes, train_scores_mean, 'o-', color="r",
	         label="Training score")
	plt.plot(train_sizes, test_scores_mean, 'o-', color="g",
	         label="Cross-validation score")

	plt.legend(loc="best")
	return plt


########################## DATA PROCESSING #############################################


categorical_data = ['Derived Existing / New','Sale Type', 
					'Split?','Opportunity Owner', 'Region', 
					'Source of Lead', 'Pricing Calculation',
					'Contract Type']


df_to_model = df
df_to_model = df_to_model[df_to_model['Sale Type'] == 'Normal Sale' ]
df_to_model = pd.get_dummies(df_to_model,columns=categorical_data, drop_first = True)

df_to_model = format_win_column(df_to_model)

import numpy as np
from sklearn.model_selection import train_test_split
train_data, validation_data = train_test_split(df_to_model, test_size=0.2)

# Running feature standardization
from sklearn.preprocessing import StandardScaler
stdsc = StandardScaler()
X_train_std = stdsc.fit_transform(train_data.iloc[:,2:-1])
X_test_std = stdsc.transform(validation_data.iloc[:,2:-1])


############################# L1 LOGISTIC REGRESSION ######################################

# Running logistic regression
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
lr = LogisticRegression(penalty='l1')
lr = lr.fit(X_train_std,train_data.iloc[:,-1])

# Cross validation test for best C param.
param_grid_lr = [
  {'C': [0.001, 0.01, 0.1, 1, 10, 100, 1000]}]

grid_lr = GridSearchCV(lr, param_grid_lr)
grid_lr.fit(X_train_std,train_data.iloc[:,-1])

print ('LR Grid best param results: ', grid_lr.best_params_)

lr_fitted = LogisticRegression(penalty='l1', C=grid_lr.best_params_['C'])
lr_fitted = lr_fitted.fit(X_train_std,train_data.iloc[:,-1])

print('Training accuracy - logistic regression:', lr_fitted.score(X_train_std, train_data.iloc[:,-1]))
print('Test accuracy - logistic regression:', lr_fitted.score(X_test_std, validation_data.iloc[:,-1]), '\n')


for i in range(0,lr_fitted.coef_.shape[1]):
	if lr_fitted.coef_[0,i] != 0:
		
		print('L1 LogReg Coefficient ', train_data.iloc[:,2:-1].columns[i],': ', lr_fitted.coef_[0,i])

############################# SVM CLASSIFICATION REGRESSION ######################################

# Running logistic regression
from sklearn.svm import SVC

clf = SVC()
#Cross validation test for best C param.
param_grid = [
  {'C': [0.001, 0.01, 0.1, 1, 10, 100, 1000], 'gamma': [0.001, 0.0001]}]

grid = GridSearchCV(clf, param_grid)
grid.fit(X_train_std,train_data.iloc[:,-1])

print ('SVC Grid best param results: ', grid.best_params_)

clf_fitted = SVC(C=grid.best_params_['C'], gamma = grid.best_params_['gamma'])

clf_fitted.fit(X_train_std,train_data.iloc[:,-1])
print('\n', 'Training accuracy - SVM:', clf_fitted.score(X_train_std, train_data.iloc[:,-1]))
print('Test accuracy - SVM:', clf_fitted.score(X_test_std, validation_data.iloc[:,-1]), '\n')

############################# NEURAL NETWORK CLASSIFICATION REGRESSION ######################################

from sklearn.neural_network import MLPClassifier
clnn = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(5, 2), random_state=1)
clnn.fit(train_data.iloc[:,2:-1],train_data.iloc[:,-1])
print('Training accuracy - NN:', clnn.score(train_data.iloc[:,2:-1], train_data.iloc[:,-1]))
print('Test accuracy - NN:', clnn.score(validation_data.iloc[:,2:-1], validation_data.iloc[:,-1]), '\n')

############################# DECISION TREE CLASSIFICATION REGRESSION ######################################
from sklearn import tree

cldt = tree.DecisionTreeClassifier(max_depth=5)
cldt.fit(train_data.iloc[:,2:-1],train_data.iloc[:,-1])
print('Training accuracy - Decision Tree:', cldt.score(train_data.iloc[:,2:-1], train_data.iloc[:,-1]))
print('Test accuracy - Decision Tree:', cldt.score(validation_data.iloc[:,2:-1], validation_data.iloc[:,-1]), '\n')

#tree.export_graphviz(cldt, out_file='tree.dot') 

######## Plotting validation curve for SVM ##################################################

X, y = stdsc.transform(df_to_model.iloc[:,2:-1]), df_to_model.iloc[:,-1]
valid_cuve(X, y, grid_lr, 'LR Validation curve').show()
valid_cuve(X, y, grid, 'SVC Validation curve').show()


################### Learning curve ####################################################

# SVC is more expensive so we do a lower number of CV iterations:

X, y = stdsc.transform(df_to_model.iloc[:,2:-1]), df_to_model.iloc[:, -1]

learn_curve(X, y, grid_lr, 'LR learning curve').show()
learn_curve(X, y, grid, 'SVC learning curve').show()