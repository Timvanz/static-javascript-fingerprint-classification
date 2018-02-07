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
#  Filename  : hist_count.py
# 
#  This script takes two directories as input. Each folder in this directory
#  should represent a website. For each website directory, a "total-count.txt"
#  should be present. The features, in this file, are counted for each set and
#  a mean and standard deviation is computed. These are plotted side by side in
#  a histogram with each feature as a bin.
#  
#  Input two directories:
#  python hist_count.py [dir1] [dir2]
#  
#  Requirements: numpy, matplotlib
# 
###############################################################################

import os
import sys
import glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
np.set_printoptions(suppress=True)

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

# This function gets all the functions (features) used from the js-functions
# file. The location of this file is hardcoded. A list of functions as strings
# is returned.
def get_dict_fp_functions():
    functions = []
    js_functions = open('../static_fp_analyser/js-functions.txt', 'r').read().split('\n')
    for line in js_functions:
        if not line.startswith('#') and line:
            functions.append(line.split(',')[0])
    # Only the following set of features was used in the paper:
    functions = ["navigator.userAgent", "navigator.language",
                 "navigator.plugins.length", "navigator.mimeTypes",
                 "navigator.javaEnabled()", "navigator.javaEnabled",
                 "navigator.doNotTrack", "window.screen.height",
                 "window.screen.width", "window.screen.colorDepth",
                 "window.screen.availLeft", "window.screen.availTop",
                 "window.screen.availWidth", ".getTimezoneOffset()",
                 ".getTimezoneOffset", ".enabledPlugin", ".suffixes",
                 ".product", ".vendor"]
    return functions

# This functions plots the actual histogram. Input arguments are:
# avg_count_total as a list of averages for the first set, std_count as the
# standard deviations belonging this set, avg_count_total_fp and std_count_fp
# do the same for the second (Fingerprinting) set and functions is the list
# of functions used. Should be the same list as used to create the averages
# in the first place. Note that for this plot, the y-axis is limited to 50.
def plot(avg_count_total, std_count, avg_count_total_fp, std_count_fp, functions):
    # N, ind and width are parameters that allow to bins to be shown side by
    # side.
    N = len(avg_count_total)
    ind = np.arange(N)
    width = 0.4
    fig, ax = plt.subplots()
    rects1 = ax.bar(ind, avg_count_total, width, align='center', yerr=std_count,
                    color='#444444', error_kw=dict(ecolor='#777777', zorder=6, capsize=5))
    rects2 = ax.bar(ind + width, avg_count_total_fp, width, align='center',
                    yerr=std_count_fp, color='#aaaaaa', error_kw=dict(ecolor='#777777', zorder=6, capsize=5))
    ax.legend(('Non-FP websites','FP websites'))
    plt.xticks(ind + width/2, functions, rotation=90)
    plt.title("Mean occurences of (partial) JS calls\nin both sets of (non-)fingerprinting websites", y=1.08)
    plt.ylabel("Occurences")
    plt.xlabel("String (JS call)")
    plt.ylim(0,50)
    plt.show()
    

if (__name__=='__main__'):
    counted = 0
    vectors = []
    counted_fp = 0
    vectors_fp = []
    functions = get_dict_fp_functions()
    domains = glob.glob(start_dir + "*/")
    domains_fp = glob.glob(start_dir_fp + "*/")
    for domain in domains:
        counted, vectors = count_domain(domain, counted, vectors, functions)
    for domain in domains_fp:
        counted_fp, vectors_fp = count_domain(domain, counted_fp, vectors_fp, functions)
    
    # The means and standard deviations are calculated from the input matrices.
    avg_vector = np.mean(vectors, 0)
    std_vector = np.std(vectors, 0)
    avg_vector_fp = np.mean(vectors_fp, 0)
    std_vector_fp = np.std(vectors_fp, 0)
    
    #avg_count_total = dict((x, float(count_total[x])/counted) for x in count_total)
    #std_count_total = dict((x, float(count_total[x])) for x in count_total)
    #avg_count_total_fp = dict((x, float(count_total_fp[x])/counted_fp) for x in count_total_fp)
    
    table = []
    
    for i in range(len(functions)):
        #print("%s: %s - %s" % (functions[i], avg_vector[i], avg_vector_fp[i]))
        table.append([functions[i], avg_vector[i], std_vector[i], avg_vector_fp[i], std_vector_fp[i]])
    
    #table = sorted(table,key=lambda x: x[3] / x[1])
    #for row in table:
        #print(row)
        #print(row[3] / row[1])
    
    #print(avg_count_total)
    #print(avg_count_total_fp)
    plot(avg_vector, std_vector, avg_vector_fp, std_vector_fp, functions)
    #print(np.round(count_total / counted, decimals=2))