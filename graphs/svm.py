###############################################################################
# 
#  GridSearch parameters for SVM classifier, classification report and ROC
#  curve plot.
# 
#  Python 3.5
#
#  Author(s) : Tim van Zalingen and Sjors Haanen
#  Date      : 7 Februari 2018
#  Course    : Research Project 1 (RP1)
#  Filename  : svm.py
# 
#  This script takes two directories as input. Each folder in this directory
#  should represent a website. For each website directory, a "total-count.txt"
#  should be present. A vector of the feature count in the file is created.
#  For all samples a GridSearch is performed to find the best SVM parameters.
#  For these SVM parameters, a classification report is shown and ROC curve
#  plotted.
#  
#  Input two directories:
#  python svm.py [dir1] [dir2]
#  
#  Requirements: numpy, scipy, matplotlib, sklearn
# 
###############################################################################

import os
import sys
import glob
from sklearn import svm
import numpy as np
import scipy as sp
np.set_printoptions(suppress=True)
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report, precision_score, recall_score, f1_score
from sklearn.model_selection import cross_val_score
from sklearn.utils import shuffle
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.model_selection import LeaveOneOut
from sklearn.model_selection import KFold
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
from sklearn.metrics import auc
from sklearn.feature_selection import SelectFromModel
import matplotlib

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

# This function is used to count for one domain or file. It returns a single
# vector and increases the amount counted.
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

def get_dict_fp_functions():
    functions = []
    js_functions = open('../static_fp_analyser/js-functions.txt', 'r').read().split('\n')
    for line in js_functions:
        if not line.startswith('#') and line:
            functions.append(line.split(',')[0])
    print(functions)
    # The functions used as described in the paper.
    functions = ["navigator.userAgent", ".userAgent", "userAgent", ".product",
                 ".vendor", "vendor", "navigator.language", ".description",
                 "description", "navigator.plugins.length", ".plugins.length",
                 "navigator.mimeTypes", ".mimeTypes", "mimeTypes",
                 "navigator.javaEnabled()", ".javaEnabled()", "javaEnabled()",
                 "navigator.javaEnabled", ".javaEnabled", "javaEnabled",
                 ".enabledPlugin", "enabledPlugin", ".suffixes", "suffixes",
                 "navigator.doNotTrack", ".doNotTrack", "doNotTrack",
                 "window.screen.height", ".screen.height",
                 "window.screen.width", ".screen.width",
                 "window.screen.colorDepth", ".screen.colorDepth",
                 ".colorDepth", "colorDepth", "window.screen.availLeft",
                 ".screen.availLeft", ".availLeft", "availLeft",
                 "window.screen.availTop", ".screen.availTop", ".availTop",
                 "availTop", "window.screen.availWidth", ".screen.availWidth",
                 ".availWidth", "availWidth", ".getTimezoneOffset()",
                 "getTimezoneOffset()", ".getTimezoneOffset",
                 "getTimezoneOffset"]
    return functions

# This function is used when classifying a new set with the trained classifier.
# It returns a single vector (sample) instead of multiple vectors (samples).
def count_domain_single_vector(path_domain, counted, functions):
    for txt_file in glob.iglob(path_domain + '**/*.txt', recursive=True):
        counted, vector = count_file(txt_file, counted, functions)
    return counted, vector

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
    # Functions allows us to determine what features are used.
    functions = get_dict_fp_functions()
    # domains is the first set of non-fingerprinting scripts
    domains = glob.glob(start_dir + "*/")
    # domains_fp is our set of fingerprinting scripts
    domains_fp = glob.glob(start_dir_fp + "*/")
    for domain in domains:
        print(domain)
        counted, vectors = count_domain(domain, counted, vectors, functions)
    for domain in domains_fp:
        print(domain)
        counted_fp, vectors_fp = count_domain(domain, counted_fp, vectors_fp, functions)
    print(vectors)
    print()
    print(vectors_fp)
    
    ###########################################################################
    # START OF THE SVM classification.
    # X is the input matrix with as length all samples, each sample is a vector
    # with features. Each vector should be the same length.
    # y is the same length as X, where each element is the result (here 0 or 1)
    # of the corresponding sample in X.
    ###########################################################################
    
    X = np.append(vectors, vectors_fp, axis=0)
    y = np.append(np.zeros(len(vectors), dtype=int), np.zeros(len(vectors_fp), dtype=int) + 1)
    
    
    X_train = X
    y_train = y
    X_test = X
    y_test = y
    
    parameters = [{'kernel': ['rbf'],
                'gamma': [1e-4, 1e-3, 0.01, 0.1, 0.2, 0.5],
                    'C': [1, 10, 100, 1000], 'class_weight': [None, 'balanced']},
                {'kernel': ['linear'], 'C': [1, 10, 100, 1000]}]

    ###########################################################################
    # GRID SEARCH
    ###########################################################################

    print("# Tuning hyper-parameters")
    print()

    clf = GridSearchCV(svm.SVC(decision_function_shape='ovr'), parameters, cv=5)
    clf.fit(X_train, y_train)
    
    for q in X:
        print(clf.predict([q]))

    print("Best parameters set found on development set:")
    print()
    print(clf.best_params_)
    print()
    print("Grid scores on training set:")
    print()
    means = clf.cv_results_['mean_test_score']
    stds = clf.cv_results_['std_test_score']
    for mean, std, params in zip(means, stds, clf.cv_results_['params']):
        print("%0.3f (+/-%0.03f) for %r"
            % (mean, std * 2, params))
    print()
    
    print("Detailed classification report:")
    print()
    print("The model is trained on the full development set.")
    print("The scores are computed on the full evaluation set.")
    print()
    y_true, y_pred = y_test, clf.predict(X_test)
    print(classification_report(y_true, y_pred))
    print()
    
    
    ###########################################################################
    # CLASSIFICATION REPORT
    # For stratified K-folds as 'repeats'.
    # 'iterations' can be set to take an average of multiple runs of the whole
    # classification.
    # clf allows classifier to be set manually instead of with GridSearchCV.
    ###########################################################################
    
    repeats = 4
    iterations = 1
    
    clf = svm.SVC(kernel='rbf', C=1000, gamma=0.0001, probability=True)
    
    print("Folded classification reports %s" % (repeats))
    print()
    average_scores = np.zeros((4,2))
    for i in range(iterations):
        cv = KFold(n_splits=repeats, shuffle=True)
        for train, test in cv.split(X, y):
            cv = StratifiedKFold(n_splits=repeats, shuffle=True)
            clf.fit(X[train], y[train])
            y_true, y_pred = y[test], clf.predict(X[test])
            cr = precision_recall_fscore_support(y_true, y_pred)
            average_scores = average_scores + (1 / (repeats * iterations)) * np.array(cr)
    print("\t   precision\trecall\tf1-score\tsupport")
    print("\t0  %.2f\t\t%.2f\t%.2f\t\t%s" % (average_scores[0][0], average_scores[1][0], average_scores[2][0], int(average_scores[3][0])))
    print("\t1  %.2f\t\t%.2f\t%.2f\t\t%s" % (average_scores[0][1], average_scores[1][1], average_scores[2][1], int(average_scores[3][1])))
    print("avg/total  %.2f\t\t%.2f\t%.2f\t\t%s" % ((average_scores[0][0] + average_scores[0][1]) / 2,
                                               (average_scores[1][0] + average_scores[1][1]) / 2,
                                               (average_scores[2][0] + average_scores[2][1]) / 2,
                                               int(average_scores[3][0] + average_scores[3][1])))
    
    
    ###########################################################################
    # Plot of the ROC curve for 4 and 2 folds
    ###########################################################################
    
    repeats = 2
    
    tprs = []
    aucs = []
    mean_fpr = np.linspace(0, 1, 100)
    
    for i in range(iterations):
        cv = StratifiedKFold(n_splits=repeats, shuffle=True)
        for train, test in cv.split(X, y):
            probas = clf.fit(X[train], y[train]).predict_proba(X[test])
            fpr, tpr, thresholds = roc_curve(y[test], probas[:, 1])
            tprs.append(sp.interp(mean_fpr, fpr, tpr))
            tprs[-1][0] = 0.0
            roc_auc = auc(fpr, tpr)
            aucs.append(roc_auc)
    
    mean_tpr = np.mean(tprs, axis=0)
    mean_tpr[-1] = 1.0
    mean_auc = auc(mean_fpr, mean_tpr)
    std_auc = np.std(aucs)
    plt.plot(mean_fpr, mean_tpr, color='#888888',
             label=r'Mean ROC (AUC = %0.2f $\pm$ %0.2f) 2 folds' % (mean_auc, std_auc),
             linestyle='-.', lw=2, alpha=.8)

    std_tpr = np.std(tprs, axis=0)
    tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
    tprs_lower = np.maximum(mean_tpr - std_tpr, 0)
    
    
    # 4 folds
    repeats = 4
    
    tprs = []
    aucs = []
    mean_fpr = np.linspace(0, 1, 100)
    
    for i in range(iterations):
        cv = StratifiedKFold(n_splits=repeats, shuffle=True)
        for train, test in cv.split(X, y):
            probas = clf.fit(X[train], y[train]).predict_proba(X[test])
            fpr, tpr, thresholds = roc_curve(y[test], probas[:, 1])
            tprs.append(sp.interp(mean_fpr, fpr, tpr))
            tprs[-1][0] = 0.0
            roc_auc = auc(fpr, tpr)
            aucs.append(roc_auc)
            plt.plot(fpr, tpr, lw=0.5, alpha=0.3, color='darkgrey')
    
    mean_tpr = np.mean(tprs, axis=0)
    mean_tpr[-1] = 1.0
    mean_auc = auc(mean_fpr, mean_tpr)
    std_auc = np.std(aucs)
    plt.plot(mean_fpr, mean_tpr, color='#222222',
             label=r'Mean ROC (AUC = %0.2f $\pm$ %0.2f) 4 folds' % (mean_auc, std_auc),
             lw=2, alpha=.8)

    std_tpr = np.std(tprs, axis=0)
    tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
    tprs_lower = np.maximum(mean_tpr - std_tpr, 0)
    plt.fill_between(mean_fpr, tprs_lower, tprs_upper, color='#888888', alpha=.2,
                 label=r'$\pm$ std. dev. 4 folds')
    

    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic Curve')
    plt.plot([0, 1], [0, 1], linestyle='--', lw=2, color='black', label='Luck', alpha=.8)
    plt.legend(loc='lower right')
    plt.show()

    
    ###########################################################################
    # This code was used to do predictions for each element from a third set.
    ###########################################################################
    
    #clf = svm.SVC(kernel='rbf', C=1000, gamma=0.0001, probability=True)
    #clf.fit(X, y)
    
    #counted_c = 0
    #domains_c = glob.glob("../static_fp_analyser/crawler-results/" + "*/")
    #for domain in domains_c:
        #print(domain)
        #counted_c, vector_c = count_domain_single_vector(domain, counted, functions)
        #print(clf.predict_proba([vector_c]))
    
    