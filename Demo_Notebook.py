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

snapshots = ['20220117']   #This is the snapshot that I want to plot, and it corresponds to the date code of
                        #the sheet in my excel workbook. This should be changed if you want to view
                        #different years or snapshots of your data.

PubPy.h_index_panels(pubs_dict, snapshots, color_map='plasma')

#To save this plot, change the file name and add a directory path to the line below. You can also change
#the type of file by changing the extension.

#plt.savefig('Hirsch_Plot_Example_20220117.png')


# %% [markdown]
# ## H-Index Comparison
# After an initial snapshot of Google Scholar data, your h-index will grow. It is useful, then, to compare Hirsch plots. The following cell constructs a panel figure with several Hirsch plots, as above, except that they all share one color bar for ease of interpretation. This portrayal of your snapshots is far more nuanced than a simple time series of your h-index as displayed above. 

# %%
#Note that I add more than 4 snapshots here, but the message generated prior to the plot explains which 4 of 5 will be plotted.
snapshots = ['20130301','20160201','20200106','20230101', '20220117']

fig, axes, h = PubPy.h_index_panels(pubs_dict, snapshots, 'plasma')

#To save the figure, delete the # before the new two lines of code and change your directory to an actual directory in your file tree, 
# and replace the leters ext with an extension that defines the file type you wish to save to (.jpg, .svg, .png, .pdf, etc.):
#directory = 'my_computer/my_directory/filename.ext'

#plt.savefig(directory)
