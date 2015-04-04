
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

# ###Importing the Data
# The training data is organized in a series of subdirectories that contain examples for the each class of interest. We will store the list of directory names to aid in labelling the data classes for training and testing purposes.

# In[3]:

# find the largest nonzero region
def getLargestRegion(props, labelmap, imagethres):
    regionmaxprop = None
    for regionprop in props:
        # check to see if the region is at least 50% nonzero
        if sum(imagethres[labelmap == regionprop.label])*1.0/regionprop.area < 0.50:
            continue
        if regionmaxprop is None:
            regionmaxprop = regionprop
        if regionmaxprop.filled_area < regionprop.filled_area:
            regionmaxprop = regionprop
    return regionmaxprop

def getRegionFeatures(image):
    image = image.copy()
    # Create the thresholded image to eliminate some of the background
    imagethr = np.where(image > np.mean(image),0.,1.0)

    #Dilate the image
    imdilated = morphology.dilation(imagethr, np.ones((4,4)))

    # Create the label list
    label_list = measure.label(imdilated)
    label_list = imagethr*label_list
    label_list = label_list.astype(int)
    
    region_list = measure.regionprops(label_list)
    maxregion = getLargestRegion(region_list, label_list, imagethr)
    
    # guard against cases where the segmentation fails by providing zeros
    ratio = 0.0
    if ((not maxregion is None) and  (maxregion.major_axis_length != 0.0)):
        ratio = 0.0 if maxregion is None else  maxregion.minor_axis_length*1.0 / maxregion.major_axis_length
    
    if maxregion is None:
        return 0.0
    else:
        return ratio, maxregion.major_axis_length, maxregion.minor_axis_length, maxregion.eccentricity,            maxregion.equivalent_diameter, maxregion.filled_area, maxregion.orientation        

# Rescale the images and create the combined metrics and training labels
def data_prep(dataset, directory_names):

#get the total training images
    numberofImages = 0
    for folder in directory_names:
        for fileNameDir in os.walk(folder):   
            for fileName in fileNameDir[2]:
             # Only read in the images
                if fileName[-4:] != ".jpg":
                    continue
                numberofImages += 1


# We'll rescale the images to be 25x25
    maxPixel = 48
    imageSize = maxPixel * maxPixel
    num_rows = numberofImages # one row for each image in the training dataset
    num_features = imageSize + 8 # for our additional features

# X is the feature vector with one row of features per image
# consisting of the pixel values and our metric
    X = np.zeros((num_rows, num_features), dtype=float)
# y is the numeric class label 
    y = np.zeros((num_rows))

    files = []
# Generate training data
    i = 0    
    label = 0
# List of string of class names
    namesClasses = list()

    print "Reading images"
# Navigate through the list of directories
    for folder in directory_names:
    # Append the string class name for each class
        currentClass = folder.split(os.pathsep)[-1]
        namesClasses.append(currentClass)
        for fileNameDir in os.walk(folder):   
            for fileName in fileNameDir[2]:
            # Only read in the images
                if fileName[-4:] != ".jpg":
                    continue
            
            # Read in the images and create the features
                nameFileImage = "{0}{1}{2}".format(fileNameDir[0], os.sep, fileName)            
                image = imread(nameFileImage, as_grey=True)
                files.append(nameFileImage)

            #Generate and Store the features in X
                X[i, imageSize:imageSize+7] = getRegionFeatures(image)
            
            # Rescale and Store the image pixels
                image = resize(image, (maxPixel, maxPixel))
                X[i, 0:imageSize] = np.reshape(image, (1, imageSize))
           
            
            # Store the classlabel
                if dataset == "Train":
                    X[i, imageSize+7] = label
                # y[i] = label
                i += 1
            # report progress for each 5% done  
                report = [int((j+1)*num_rows/20.) for j in range(20)]
                if i in report: print np.ceil(i *100.0 / num_rows), "% done"
        label += 1

    print "Dumping %s as hkl" %dataset
    hickle.dump(X,"{}.hkl".format(dataset))

# get the classnames from the directory structure
directory_names = list(set(glob.glob(os.path.join("train", "*")) ).difference(set(glob.glob(os.path.join("train","*.*")))))
dataset="Train"
print "Calling data prep for %s" %dataset
data_prep(dataset, directory_names)

# file_names = glob.glob("/home/shankarmsy/Documents/DataSci/git_home/Public/kaggle_Data_Science_Bowl/test/*.jpg")
# directory_names = list(set(glob.glob(os.path.join("test", "*")) ).difference(set(glob.glob(os.path.join("test","*.*")))))
# dataset="Test"
# print "Calling data prep for %s" %dataset
# data_prep(dataset, directory_names)

