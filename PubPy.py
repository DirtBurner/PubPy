import pandas as pd
import matplotlib.pyplot as plt

def get_publication_data(file):
    pubs_dict = pd.read_excel(file, sheet_name=None)
    pubs_snapshot_list = list(pubs_dict.keys())
    print('Your available publication snapshot dates are: ', pubs_snapshot_list)

    return pubs_dict, pubs_snapshot_list


def calculate_H_index(data):
    '''
    Calculates the H-index as defined by the intersection of the 1:1 line between citations and number of publications
    and the rank of publicaitons ordered in decreasing number of citations. That means that publication 1 has 
    the most citations and publication n has the least. 

    Inputs:
        data (dataframe)
            One sheet from the excel spreadsheet containing the historical Google scholar Hirsch plot data.
    
    Outputs:
        h (integer)
            This is the H-index calculated using the standard method.
        sorted_data (dataframe)
            Same as data input, however it is sorted on 'Citations' in descending order. It is useful to return
            this variable for use in the plot_Hirsch function.
    '''
    #Sort data - spreadsheet should contain sorted data, but this is just in case.
    sorted_data = data.sort_values(by='Citations', ascending=False, ignore_index=True)
    ctr = 1
    for datum in sorted_data.iterrows():
        if  ctr <= datum[1]['Citations']:
            h = ctr
            ctr += 1
        else:
            break

    return h, sorted_data

def h_index_time_series(pubs_dict):
    '''
    This function generates a time series by calculating the h-index from every dataframe in the pubs_dict, a dictionary
    in which each value is a dataframe of publication information from your publication snapshot. 

    Inputs:
        pubs_dict (dictionary of dataframes)
            The dictionary output from get_publication_data. Each key is the date code (str, YYYYMMDD) of the publication and 
            citation snapshot from each sheet in your excel workbook, and the values are the DataFrames loaded from those
            corresponding sheets.

    Outputs:
        ts_df (dataframe) 
            This is the DataFrame of the time series. It contains two columns, Date and h-index.
            Date is in pandas datetime format, converted from the datecode (YYYYMMDD) from each
            tab in your snapshot spreadsheet.

    '''

    #Create time series dataframe with dates and h-indices from each date, start with empty lists 
    #for each column.
    date_list = []
    h_list = []
    for k,v in pubs_dict.items():
        h_temp, _ = calculate_H_index(v)
        date_temp = pd.to_datetime(k)
        date_list.append(date_temp)
        h_list.append(h_temp)

    ts_df = pd.DataFrame({'Date':date_list, 'h-index':h_list})

    fig, ax = plt.subplots(nrows=1, ncols=1)

    ax.plot(
        ts_df['Date'],
        ts_df['h-index'],
        linestyle='-',
        mfc='lightblue',
        marker='d',
        mec='k',
        color='k',
        markersize=15
    )

    ax.set(xlabel='Date', ylabel='h-index')
    ax.xaxis.get_label().set_fontsize(16)
    ax.yaxis.get_label().set_fontsize(16)

    return ts_df, ax


def plot_Hirsch(data, fig, axis, year, cmap='inferno'):
    '''
    Plots individual Hirsch plot into defined matplotlib axis

    Inputs:
        data (dataframe)
            One sheet from the excel spreadsheet containing the historical Google scholar Hirsch plot data. Data
            should be sorted on number of citations from largest to smallest (ascending=False). Generally, 
            spreadsheet will be organized this way, however the function 'calculate_H_index' also sorts the data.
            Thus, one can use the return of that function, sorted_data, as the input for this function to be 
            certain. 
        fig (figure)
            figure from subplot set up in notebook cell
        axis (matplotlib axes or subplots.AxesSubplot)
            The axes onto which you want to the plot the Hirsch plot data
        year (string, YYYYMMDD)
            Year passed in from the iterations through the dictionary of sheets in the excel spreadsheet 
            containing the data. For each plot, this year should correspond to the first 4 characters of the 
            strings (YYYYMMDD) that denote the sheets of the excel worksheet.
        cmap (colormap, default viridis)
            The color map of the Hirsch plot

    '''
    h, sorted_data = calculate_H_index(data[year])
    year_num = int(year[:4])
    annotation_dict = {'family':'arial', 'size':14}

    hirsch_plot = axis.scatter(
        sorted_data.index,
        sorted_data['Citations'],
        c=sorted_data['Year'],
        cmap=cmap,
        vmin=min(sorted_data['Year']),
        vmax=max(sorted_data['Year']), 
        s=25*(sorted_data['Citations']+5)/(year_num-sorted_data['Year']+1),
        marker='o',
        edgecolor='k'
    )
    axis.plot(sorted_data.index, sorted_data.index, color='k')
    axis.set(xlabel='Rank (Descending order of citations)', ylabel='Citations')
    axis.xaxis.get_label().set_fontsize(16)
    axis.yaxis.get_label().set_fontsize(16)
    axis.xaxis.get_label().set_fontname('Arial')
    axis.yaxis.get_label().set_fontname('Arial')
    ylimits = axis.get_ylim()
    xlimits = axis.get_xlim()
    axis.text(0.5*max(xlimits), 0.75*max(ylimits),'H-index = '+str(h)+',\n '+year[4:6]+'/'+year[6::]+'/'+year[:4], fontdict=annotation_dict)    
    cbar = fig.colorbar(hirsch_plot, shrink=0.95)
    cbar.ax.set_ylabel(ylabel='Year published', fontfamily='arial', fontsize=16)
    

    return h, hirsch_plot

def axis_limit_search(lims, min_max_axis):
    '''
    Takes assigned axes limits, searches whether min amd max are less than or greater than min and max of 
    universal limits (respectively) and replaces if min and/or max are exceeded. Output is largest range in 
    axes limits that can be used in all subplots without omitting data. 
    '''
    if max(lims) > max(min_max_axis):
        min_max_axis[1] = max(lims)
    if min(lims) < min(min_max_axis):
        min_max_axis[0] = min(lims)
    
    return min_max_axis

def adjust_subplot_axes(axes, axis='x'):
    '''
    Finds the minimum and maximum of x-axes from each subplot and makes all subplots equal along that axis.

        Inputs:
            axes: The axes which you will adjust. In a matplotlib suplot these are in lists of several axes
                when you plot more than one subplot (nrows and/or ncols > 1).
            axis (string 'x', 'y', or 'both'): Choose axis you wish to adjust in your subplots. Both runs the
                loop twice. Anything by these three strings results in an error message and no action.

        Outputs:
            min_max: (dictionary of lists of floats) a 2-member list of floats depicting the minimum and
                maximum of an axis.

    '''
    lims_dict = {}

    min_max_x = [0,0]
    min_max_y = [0,0]

    for ax in axes.flatten():
        if (axis == 'x') | (axis == 'both'):
            lims = ax.get_xlim()
            min_max_x = axis_limit_search(lims, min_max_x)
            lims_dict |= {'x':min_max_x}
        if (axis == 'y') | (axis == 'both'):
            lims = ax.get_ylim()
            min_max_y = axis_limit_search(lims, min_max_y)
            lims_dict |= {'y':min_max_y}
        if (axis != 'both') & (axis != 'x') & (axis != 'y'):
            print('No action taken! Please enter x, y, or both for kwarg axis= !')

    for k, v in lims_dict.items():
        if k == 'x':
            for lims in axes.flatten():
                lims.set_xlim(v)
        if k == 'y':
            for lims in axes.flatten():
                lims.set_ylim(v)
    
    return lims_dict

