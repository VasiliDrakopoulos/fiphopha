# FiPHoPHA - A Fiber Photometry Python Package for Post-Hoc Analysis

This Python tool allows for the analysis of photometry data, enabling the user to upload Excel files, select baseline and comparison periods, and calculate significant differences within and between-groups. The tool performs both bootstrapping to derive confidence intervals as well as permutation tests.

## Cite (https://www.biorxiv.org/content/10.1101/2025.06.12.659422v1)

## Features

- **Excel Integration:** Load photometry data from Excel, analyze it, and save the results back to an Excel file.
- **Graphical User Interface (GUI):** The application uses a simple GUI for file uploads, setting periods, and saving results.
- **Within and Between-Groups Bootstrapped Confidence Intervals (CI):** Comparison to baseline is determined by whether the bootstrapped CI includes the null of 0. Whilst comparison for within-groups is determined from subtracting each corresponding animal/trial of the group and bootstrapping the product to derive CIs and determining deviation from the null of 0. For between-groups the distribution of each group is bootstrapped and subtracted, then CIs derived and determined if they deviate from the null of 0
- **Permutation Test:** Permutation tests are used to compare differences between groups and determine significance.


## How to Use

1. **Load Excel Data:** Click the "Load Excel File" button to load your photometry data in `.xlsx` format.
2. **Set Baseline and Comparison Periods:** Enter the row indices for the baseline and comparison periods.
3. **Analyze Data:** The application will analyze the loaded data, calculating bootstrapped confidence intervals and performing permutation tests between groups.
4. **Save Results:** Save the analyzed results to an Excel file, which includes confidence intervals, significance maps, and significant timings.

### Excel File Structure

- **Sheets:** Timings, where each row corresponds to a Z-score of that time point and columns represent individual animals/trials.
- **Subsequent Sheets represent different groups of animals** 

### Installation Instructions in Any Environemnt

1. **Install package:** 
```bash
pip install fiphopha
```
2. **Run main script:** 
```bash
fiphopha
```

## Dependencies

- **NumPy**
- **Pandas**
- **Scikit-learn**
- **Tkinter** 
- **Setuptools**
- **Openpyxl**

## Acknowledgements
Adapted from Dr. Philip Jean-Richard Dit Bressel from the University of New South Wales
Jean-Richard-Dit-Bressel, P., Clifford, C. W. G., & McNally, G. P. (2020). Analyzing Event-Related Transients: Confidence Intervals, Permutation Tests, and Consecutive Thresholds. Frontiers in molecular neuroscience, 13, 14. https://doi.org/10.3389/fnmol.2020.00014

I would also like to thank all members of the Andrews Lab at Monash University for being testers of the scripts.
