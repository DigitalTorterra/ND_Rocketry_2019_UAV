from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
import numpy as np
import pickle

dataset = np.load('dataset.npy')
#[Aspect Ratio, Rotated Extent, Solidity, Compactness, Eccentricity, Log Hu Moments 1-7, Label]
#3487x13
np.random.shuffle(dataset)

X_train = dataset[:3000,:12]
X_test = dataset[3000:,:12]
y_train = dataset[:3000,12].astype(np.float64)
y_test = dataset[3000:,12].astype(np.float64)

svm_clf = Pipeline((
	('scaler',StandardScaler()),
	('linear_svc',LinearSVC(C=1,loss='hinge'))
))

svm_clf.fit(X_train,y_train)

print(svm_clf.score(X_test, y_test))

filename = 'finalized_model.sav'
pickle.dump(svm_clf, open(filename,'wb'))

loaded_model = pickle.load(open(filename, 'rb'))
result = loaded_model.score(X_test, y_test)
print(result)