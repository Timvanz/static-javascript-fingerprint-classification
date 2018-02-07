# Plots

All scripts take two directories. The first should contain non-fingerprinters
and the second should contain fingerprinters.

## Histogram of given features
```
python hist_count.py [dir1] [dir2]
```
Note that the features used are either hardcoded in the file or all features
are used.

## Scatter Plot
```
python scatter_plot.py [dir1] [dir2]
```
Scatter plot and 2D linear SVM classification between two directories for two
given features. These features are currently hardcoded in the file.

## SVM classification
```
python svm.py [dir1] [dir2]
```
Given two directories of samples: Gridsearch for SVM parameters.
Classification report with these parameters. ROC curve plot and AUC
calculation.