
# coding: utf-8

# ##Predicting Ocean Health by identifying Planktons
# Below is my approach to solving the National Data Science Bowl competition hosted by Kaggle and borrows from the excellent starter code by Aaron Sanders. 
# 
# The goal of this competition hosted by Booz Allen Hamilton, simply put, is to identify various classes of Planktons from provided under-sea images, that will allow measuring and monitoring of Plankton populations. Rest assured, the task is nowehere close to as easy as it sounds. The competition page provides an excellent summary of the challenge as well as an introduction to why we should care about Planktons. Below is a quick paragraph that explains the competition: 
# 
# >The National Data Science Bowl challenges you to build an algorithm to automate the image identification process. Hatfield scientists have prepared a large collection of labeled images, approximately 30k of which are provided as a training set. Each raw image was run through an automatic process to extract regions of interest, resulting in smaller images that contain a single organism/entity. You must create an algorithm that assigns class probabilities to a given image.
# 
# If you needed to understand what this challenge is about, download the data and take a peek into the test folder :\
# 
# Without further ado, let's begin with Aaron's setup to start reading the dataset.

# In[9]:

#Import required Python modules
from skimage.io import imread
from skimage.transform import resize
from sklearn.ensemble import RandomForestClassifier as RF
import glob
import os
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.svm import SVC
from sklearn.multiclass import OneVsRestClassifier
from sklearn import cross_validation
from sklearn.preprocessing import StandardScaler
from sklearn.cross_validation import StratifiedKFold as KFold, cross_val_score, LeaveOneOut
from sklearn.metrics import classification_report, make_scorer
from matplotlib import pyplot as plt
from matplotlib import colors
from pylab import cm
from skimage import segmentation
from skimage.morphology import watershed
from skimage import measure
from skimage import morphology
import numpy as np
import pandas as pd
from scipy import ndimage
from skimage.feature import peak_local_max
from sklearn.cross_validation import StratifiedShuffleSplit
from sklearn.grid_search import GridSearchCV
import pickle, hickle
from datetime import datetime
import sys

selection=raw_input("Which Estimator (ET, RF, SVM, LO)?")
scale=raw_input("Scale (y/n)?")

sys.stdout = open("gridsearch_logs_{}".format(selection), "a")

print "New Gridsearch commenced at %s" %datetime.now()

print "Loaded Train from hickle"
#Load X and y. 
X =hickle.load('Train.hkl')
X,y=X[:,:-1],X[:,-1:].ravel() 


# get the classnames from the directory structure
directory_names = list(set(glob.glob(os.path.join("train", "*"))\
 ).difference(set(glob.glob(os.path.join("train","*.*")))))

namesClasses=list()
for folder in directory_names:
    # Append the string class name for each class
    currentClass = folder.split(os.pathsep)[-1]
    namesClasses.append(currentClass)

# **10% Holdout set**  
# Let's reserve 10% as a holdout set. We'll not use this dataset until we're ready to submit a model.

hold_shuffle=StratifiedShuffleSplit(y, n_iter=1, test_size=0.1, random_state=48)

for train, test in hold_shuffle:
    X_train, X_test, y_train, y_test = X[train,:], X[test,:], y[train], y[test]

print X_train.shape, X_test.shape, y_test.shape, y_test.shape

# **StratifiedShuffleSplit Cross-Validation**   
# Now let's firstly define the module that will perform cross validation and return the best classifier. This will use the same StratifiedShuffleSplit and run cv for specified iterations and test sizes. We will call upon this module for each model we fit to the dataset.

# In[18]:

def multiclass_log_loss(y_true, y_pred):
    """Multi class version of Logarithmic Loss metric.
    https://www.kaggle.com/wiki/MultiClassLogLoss

    Parameters
    ----------
    y_true : array, shape = [n_samples]
            true class, intergers in [0, n_classes - 1)
    y_pred : array, shape = [n_samples, n_classes]

    Returns
    -------
    loss : float
    """
    eps=1e-15
    predictions = np.clip(y_pred, eps, 1 - eps)

    # normalize row sums to 1
    predictions /= predictions.sum(axis=1)[:, np.newaxis]

    actual = np.zeros(y_pred.shape)
    n_samples = actual.shape[0]
    actual[np.arange(n_samples), y_true.astype(int)] = 1
    vectsum = np.sum(actual * np.log(predictions))
    loss = -1.0 / n_samples * vectsum
    return loss

def CrossValidate(estimator, param_grid, n_iter, test_size, n_jobs):

#Choose cross-validation generator - let's choose ShuffleSplit which randomly shuffles and selects Train and CV sets
#for each iteration. There are other methods like the KFold split.
    cv = StratifiedShuffleSplit(y_train, n_iter=n_iter, test_size=test_size)

#Apply the cross-validation iterator on the Training set using GridSearchCV. This will run the classifier on the 
#different train/cv splits using parameters specified and return the model that has the best results

#Note that we are tuning based on Classification Accuracy, which is the metric used by Kaggle for evaluating results for 
#this competition. Ideally, we would use a better metric such as the mean-squared error.
    classifier = GridSearchCV(estimator=estimator, cv=cv, param_grid=param_grid, n_jobs=n_jobs, scoring='log_loss')

#Also note that we're feeding multiple neighbors to the GridSearch to try out.

#We'll now fit the training dataset to this classifier
    classifier.fit(X_train, y_train)

#Let's look at the best estimator that was found by GridSearchCV
    print "Best Estimator learned through GridSearch"
    print classifier.best_estimator_
    
    return cv, classifier.best_estimator_


# **Random Forests**  
# Before we do any exhaustive grid search I'd like to first understand how well a basic RF model performs on this dataset. Let's start with 100 estimators and rest of the parameters at default. We will crossvalidate with 3 iterations and the 80/20 split we setup earlier.

# In[19]:

#WARNING - THIS MIGHT TAKE A WHILE TO RUN. TRY ADJUSTING parameters such as n_jobs (jobs to run in parallel, before 
#increasing this make sure your system can handle it).

#SELECT INTERRUPT IN THE MENU AND PRESS INTERRUPT KERNEL IF YOU NEEDD TO STOP EXECUTION


if scale == 'y':
    print "Scaling train and test"
    scale=StandardScaler()
    X_train = scale.fit_transform(X_train)
    X_test = scale.fit_transform(X_test)

if selection=="ET":
    estimator=ExtraTreesClassifier()
    param_grid={'n_estimators': [100], #[100, 1000, 5000],
                'max_depth': [8, 10, 14]
#               'max_features': None,
#               'oob_score': ['True']
#               'n_jobs': [4]
           }

if selection=="SVC":
    estimator=SVC(kernel='rbf', probability=True)
    param_grid={'C': [.1, .3, 1], #[100, 1000, 5000],
                'gamma': [.03, .1, .3]
           }
    
n_jobs=1
n_iter=10
test_size=0.2

#Let's fit RF to the training dataset by calling the function we just created.
# cv,best_estimator=CrossValidate(estimator, param_grid, n_iter, test_size, n_jobs)

best_estimator=ExtraTreesClassifier(bootstrap=False, compute_importances=None,
           criterion='gini', max_depth='auto', max_features='auto',
           max_leaf_nodes=None, min_density=None, min_samples_leaf=1,
           min_samples_split=2, n_estimators=1000, n_jobs=-1,
           oob_score=False, random_state=None, verbose=0)

best_estimator.fit(X_train, y_train)

# The log loss isn't all that great. Let's generate the classification report for the training set (X,y).

y_pred=best_estimator.predict(X_train)
print "Classification Report (Training)"
print classification_report(y_train, y_pred, target_names=namesClasses)

print "Log Loss (Train) = %.2f" %multiclass_log_loss(y_train, best_estimator.predict_proba(X_train))

y_pred=best_estimator.predict(X_test)
print "Classification Report (Holdout)"
print classification_report(y_test, y_pred, target_names=namesClasses)

print "Log Loss (Test) = %.2f" %multiclass_log_loss(y_test, best_estimator.predict_proba(X_test))

# **Support Vector Classifier**  
# Let's now try a Support Vector Classifier to see how the initial results pan out.



