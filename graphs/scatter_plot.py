###############################################################################
# 
#  Plot a histogram of mean occurences (with standard deviation) of JavaScript
#  calls from two sets.
# 
#  Python 3.5
#
#  Author(s) : Tim van Zalingen and Sjors Haanen
#  Date      : 7 Februari 2018
#  Course    : Research Project 1 (RP1)
#  Filename  : scatter_plot.py
# 
#  This script takes two directories as input. Each folder in this directory
#  should represent a website. For each website directory, a "total-count.txt"
#  should be present. For two given features, a scatter plot is created and a
#  linear SVM classification performed and shown in the plot. These features
#  are hardcoded inside this file.
#
#  Future work is moving what features are shown from hardcoded to command line
#  argument.
#  
#  Input two directories:
#  python scatter_plot.py [dir1] [dir2]
#  
#  Requirements: numpy, scipy, matplotlib, sklearn
# 
###############################################################################

import os
import sys
import glob
import itertools
import numpy as np
import scipy as sp
np.set_printoptions(suppress=True)
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib
from sklearn import svm

# Font size is increased because these plots are used in a slidedeck and
# two-column paper.
matplotlib.rcParams.update({'font.size': 16})


# Check of whether the arguments are correct.
if len(sys.argv) != 3:
    print("Needs exactly 2 argument: Two directories containing directories \
of domains")
    sys.exit(1)
if not os.path.isdir(sys.argv[1]):
    print("{0} is not a directory.".format(sys.argv[1]))
    sys.exit(2)
if not os.path.isdir(sys.argv[2]):
    print("{0} is not a directory.".format(sys.argv[2]))
    sys.exit(2)

# Making sure the directories end with "/".
start_dir = sys.argv[1]
if not start_dir.endswith("/"):
    start_dir += "/"
start_dir_fp = sys.argv[2]
if not start_dir_fp.endswith("/"):
    start_dir_fp += "/"

# Creates a vector (sample) of the current file.
def count_file(txt_file, counted, functions):
    score_file = open(txt_file, 'r')
    vector = []
    current = {}
    for line in score_file:
        count = np.array(line.split(','))
        if (current == None):
            current = {}
            current[count[0]] = count[1].astype(np.int)
        elif (count[0] in current):
            current[count[0]] = current[count[0]] + count[1].astype(np.int)
        else:
            current[count[0]] = count[1].astype(np.int)
    for function in functions:
        vector.append(current[function])
    return counted + 1, vector

# This function counts for a given domain, appends this sample to the set of
# vectors (samples) and then returns the vectors.
def count_domain(path_domain, counted, vectors, functions):
    for txt_file in glob.iglob(path_domain + '**/*.txt', recursive=True):
        counted, vector = count_file(txt_file, counted, functions)
        vectors.append(vector)
    return counted, vectors

if (__name__=='__main__'):
    counted = 0
    vectors = []
    counted_fp = 0
    vectors_fp = []
    
    # These two functions were used in the presentation on 6 Februari 2017.
    #functions = [".colorDepth", ".enabledPlugin"]
    functions = [".length", "type"]
    
    domains = glob.glob(start_dir + "*/")
    domains_fp = glob.glob(start_dir_fp + "*/")
    for domain in domains:
        print(domain)
        counted, vectors = count_domain(domain, counted, vectors, functions)
    for domain in domains_fp:
        print(domain)
        counted_fp, vectors_fp = count_domain(domain, counted_fp, vectors_fp, functions)
    
    # The full set used for classification.
    X = np.append(vectors, vectors_fp, axis=0)
    y = np.append(np.zeros(len(vectors), dtype=int), np.zeros(len(vectors_fp), dtype=int) + 1)
    
    # The matrices are swapped to allow them to be scatter plotted.
    vectors = np.swapaxes(np.array(vectors), 0, 1)
    vectors_fp = np.swapaxes(np.array(vectors_fp), 0, 1)
    print(vectors)
    print(vectors_fp)
    print()
    
    # A small random value is added to more easily distinguish different
    # points.
    vectors = vectors + np.random.random_sample(vectors.shape) / 5
    vectors_fp = vectors_fp + np.random.random_sample(vectors_fp.shape) / 5
    
    # The linear SVM classification is fitted.
    clf = svm.SVC(kernel='linear',  gamma=0.7, C=1)
    clf.fit(X, y)
    
    # The line corresponding to the classification is calculated.
    w = clf.coef_[0]
    a = -w[0] / w[1]
    xx = np.linspace(0, np.amax(X))
    yy = a * xx - (clf.intercept_[0]) / w[1]
    
    # The classification and scatterplots
    plt.plot(xx, yy, 'k-')
    plt.scatter(vectors_fp[0], vectors_fp[1], color='#aa2222', marker='x', label='FP')
    plt.scatter(vectors[0], vectors[1], color='#000000', marker='.', label='No FP')
    
    plt.xlabel(functions[0])
    plt.ylabel(functions[1])
    plt.title('Occurences in JS code per website.\nLinear classification by SVM.')
    #plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, borderaxespad=0.)
    plt.legend(loc=2)
    
    xmin, xmax = plt.xlim()
    ymin, ymax = plt.ylim()
    
    # For the .colorDepth and .enabledPlugin plot, these settings should be
    # enabled:
    #plt.xlim(-0.02, 3)
    #plt.ylim(-0.5, 12)
    #plt.xticks([0,1,2,3])
    
    plt.show()
    