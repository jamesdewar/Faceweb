from sklearn.grid_search import GridSearchCV
from sklearn.svm import SVC
#Once the image has been passed through the ConvNet, we will pass the vector through a classifier (SVM)
#to get a identity for that person.



def trainSVM(data,identity):
	param_grid = [
			{'C' : [1,10,100,1000],
				'kernel' : ['linear']},
			{'C' : [1,10,100,1000],
				'gamma' : [0.001,0.0001],
				'kernel' : ['rbf']}
	]	
	trained_svm  = GridSearchCV(SVC(C=1),param_grid,cv=2).fit(data,identity)
	return trained_svm
