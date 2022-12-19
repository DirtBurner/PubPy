# %% [markdown]
# # PubPy Demonstration Notebook
#
# If you are an academic, your career will be judged by administrators who know little about your field (despite their best efforts) and who rely on publication indices. Therefore, it is important to know your publication and citation history better than anyone who may be evaluating your performance as an academic. I have built this repository and a package of python functions that generates plots and other information to put your publication and citation history into a clear perspective. It is useful for annual evaluations, promotion, and tenure, and involves simply in you manually updating your data from Google Scholar by creating a new tab on an Excel spreadsheet and adding new publications with updated citation information. 
#
# This Jupyter notebook demonstrates the functions in PubPy and their outputs. It is included in the repository as a .py file and can be opened as a Jupyter notebook using Jupytext in most environments. I recommend you simply rename this notebook and point it towards your publication data instead of `H_Index_Rosenheim_Demo.xlsx` to generate a record of your publications and citations. You can use `H_Index_Rosenheim_Demo.xlsx` to generate your publication and citation history data by simply changing the file name, deleting the extraneous tabs of my citation information, and adding tabs of your own data from Google Scholar. Because the data on Google Scholar are cumulative, this exercise in and of itself provides a valuable snapshot of past research productivity.
#
# ## Calculating the Hirsch Index
# The first demonstration simply calculates your Hirsch Index, commonly known as the H-index.

# %%
#Load Python Packages
import PubPy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#Pull in data from excel spreadsheet named in variable `filename`
filename = 'H_Index_Rosenheim_Demo.xlsx'    #Change this to the file containing your publication data.
pubs_dict, pubs_snapshot_list = PubPy.get_publication_data(filename)

#Your excel notebook data are now in a dictionary with keys being the date codes printed below (pubs_snapshot_list) and values being DataFrames of your data.
#Calculate the h-index from the last year in the snapshots:
h, sorted_pubs_df = PubPy.calculate_H_index(pubs_dict[pubs_snapshot_list[-1]])
print('H-index for ', pubs_snapshot_list[-1], ' = ', h)






# %% [markdown]
# ## Generate Time Series of H-Index
#
# Calculating an h-index is redundant with what Google Scholar already tells you, but you can now go back and see what your h-index was in previous years from previous snapshots. The next cell shows you a timeseries of your h-index, which is good to compare to h-index predictions like the [Acuna, Allesina, and Kording (2012) method](https://www.nature.com/articles/489201a#Sec1)$^1$. There is a variable for the axes handles returned by this function if you wish to add a predition for comparison. 
#
# $^1$ There used to be a calculator linked to this article. As of December 2022, it was no longer functioning. Other studies of the h-index which are more recent are also more complex and seem to not produce a calculator for individual predictions. If you cannot find a prediction, this is also a good space to put your own forecast in to a .csv file formatted like `Rosenheim_AAK_forecast_2013.csv`. Over the years following your own prediction/wish, you can see how it is playing out. 

# %%
ts_df, ts_ax = PubPy.h_index_time_series(pubs_dict, prediction='Rosenheim_AAK_forecast_2013.csv')



# %% [markdown]
# ## Visualize the H-Index
#
# Many administrators and academics use the h-index, but few visualize how it is calculated. This a useful exercise to see how one's h-index is impacted by certain publications and how other publications do not contribute to it. One can also visualize which publications contribute to the h-index fastest versus those which take a while to "catch fire."
#
# The next cell visualizes the h-index from one snapshot. The cell below that shows how you can visualize the growth of your h-index through time in a richer context than the time series above.

# %%
#Here, instead of creating an axes incident in the function and returning it, we create the axes first and 
#then populate it with information from the snapshot. This makes more sense in the plot below, but we start
#with this one first.

snapshot = '20220117'
fig, h_ax = plt.subplots(nrows=1, ncols=1)

PubPy.plot_Hirsch(pubs_dict, fig, h_ax, snapshot, cmap='inferno')

