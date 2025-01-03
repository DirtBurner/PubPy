import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

print('[][*][][*][][*][][*][]][*][][*][][*][][*][][*][][*]')
print('PubPy - Tracking your "progress" better than your administrators are.')

#Font dictionaries to set up different output styles 
axis_label_dict = {
    'fontfamily':'arial',
    'fontsize':16
}
date_annotation_dict = {
    'fontfamily':'arial',
    'fontsize':14
}
h_index_annotation_dict = {
    'fontfamily':'arial',
    'fontsize':14,
    'fontstyle':'italic'
}

DEBUG = False   #Default - this can be toggled from a notebook or another call of this package

def debug(*args):
    if DEBUG == True:
        print(args)


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

def h_index_time_series(pubs_dict, prediction=None):
    '''
    This function generates a time series by calculating the h-index from every dataframe in the pubs_dict, a dictionary
    in which each value is a dataframe of publication information from your publication snapshot. 

    Inputs:
        pubs_dict (dictionary of dataframes)
            The dictionary output from get_publication_data. Each key is the date code (str, YYYYMMDD) of the publication and 
            citation snapshot from each sheet in your excel workbook, and the values are the DataFrames loaded from those
            corresponding sheets.
        prediction (string)
            file name (including directory) of any file that you have h-index predictive data in. The
            prediction calculator I used in 2013, Acuna, Allesino, and Kording 2012 (Nature) no longer
            seems to exist except in someone's R code. I may try to reproduce it here in the future, 
            but there may be other ways to find a predictor and hence I leave this option as a keyword
            argument. You need not enter this argument - the routine will still work. Columns must be
            Year | h-index spelled as such, and file must be .csv. Extra columns simply won't be analyzed.
            Obviously, the best way to use this feature is to rename my example file and enter your data.
            Also, data can be fictitious - i.e. based on your hopes and goals. 

    Outputs:
        ts_df (dataframe) 
            This is the DataFrame of the time series. It contains two columns, Date and h-index.
            Date is in pandas datetime format, converted from the datecode (YYYYMMDD) from each
            tab in your snapshot spreadsheet.

    '''

    #Determine how plotting will work depending on the inclusion of a prediciton or not. Default is 
    #`Rosenheim_AAK_forecast_2013.csv` which works for my example data.
    if prediction:
        print('Including predictive data for comparison to snapshot data. Leave keyword argument out of function call if you do not want predictive data shown.')
        line_style = 'None'
        prediction_data = pd.read_csv(prediction)
        legend_list = ['Google scholar data', 'Prediction']
        years_datetime = pd.to_datetime(prediction_data['Year'], format='%Y')
    else:
        print('No predictive data entered, plotting only snapshot data.')
        line_style = '-'
        legend_list = ['Google scholar data']
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
    fig.patch.set_facecolor('white')
    ax.plot(
        ts_df['Date'],
        ts_df['h-index'],
        linestyle=line_style,
        mfc='lightblue',
        marker='d',
        mec='k',
        color='k',
        markersize=15
    )

    #Add prediction if present:
    if prediction:
        ax.plot(
            years_datetime,
            prediction_data['h-index'],
            linestyle='-',
            color='k'            
        )

    ax.set(xlabel='Date', ylabel='h-index')
    ax.xaxis.get_label().set_fontsize(16)
    ax.yaxis.get_label().set_fontsize(16)
    font = matplotlib.font_manager.FontProperties(
        family='arial',
        size=14        
    )
    
    ax.legend(legend_list, prop=font)

    return ts_df, ax


def plot_Hirsch(data, axis, year, cbar_limits, cmap='inferno'):
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
        cbar_limits (tuple): The high and low publication year limits for the entire batch of data being plotted in 
            this and subsequent calls to this function - there needs to be a universal limit for when this function
            is called in a loop with different years' data.
        cmap (colormap, default inferno)
            The color map of the Hirsch plot

    '''
    h, sorted_data = calculate_H_index(data[year])
    year_num = int(year[:4])
    
    hirsch_plot = axis.scatter(
        sorted_data.index,
        sorted_data['Citations'],
        c=sorted_data['Year'],
        cmap=cmap,
        vmin=cbar_limits[0],
        vmax=cbar_limits[1], 
        s=25*(sorted_data['Citations']+5)/(year_num-sorted_data['Year']+1),
        marker='o',
        edgecolor='k'
    )

    axis.plot(sorted_data.index, sorted_data.index, color='k')
    
    

    return h, hirsch_plot

def limits_search(good_list, pubs_dict):
    '''
    This replaces axis_limits_search, which used the get_xlim and get_ylim functions AFTER generation of a subplot.
    This function will rely on the data used to make the plot, allowing the subplots to all be created with known
    limits on either axes. This makes annotation and formating much easier. 

        Inputs:
            good_list (list of strings): list of YYYYMMDD codes referring to tabs in spreadsheet. These are the tabs
                that will compile the plot (max 4). Therefore, these are the publication dfs that matter for determining
                the axes and colorbar limits.
            pubs_dict (dictionary of dataframes): The dictionary that is created by reading the spreadsheet tabs. This 
                has all of the data, but the only the data with keys in good_list will be used because only that will
                be plotted. 
    '''
    for m, year in enumerate(good_list):
        pubs = pubs_dict[year]
        lims_dict = {}

        x_max = len(pubs['Year'])
        y_max = 10*(np.ceil(max(pubs['Citations'])/10))
        
        if m == 0:
            min_max_x = [-2, x_max]
            min_max_y = [-20, y_max]
        else:
            if x_max >= min_max_x[1]:
                min_max_x = [-2, x_max]  #Write new values to the max x limit only if it is bigger in the next year
            if y_max >= min_max_y[1]:
                min_max_y = [-20, y_max]

    #Get color bar limits from existing function:
    cbar_limits = pub_year_limits(pubs_dict, good_list)

    #Make dict for x and y limits:
    lims_dict |= {'x':min_max_x, 'y':min_max_y}
        
    return lims_dict, cbar_limits

def pub_year_colorbar_ticks(pub_year_lims):
    '''
    This function determines the amount of years to label the color bar y-axis with. This ensures that
    years are whole numbers and that the axis is not too crowded (max 7 divisions).

        Inputs:
            pub_year_lims (tuple): minimum and maximum from publication years, from pub_year_limits output
        Outputs:
            pub_year_list (list): list of years to use as tick mark labels on color bar axis.
    
    '''
    
    #Decide how may colorbar ticks to create by determining the time between limits.
    debug('Limits of publication years are in format: ', pub_year_lims)
    pub_year_range = max(pub_year_lims) - min(pub_year_lims)
    debug('Publication year range: ', pub_year_range)

    if pub_year_range <= 6:
        pub_year_list = list(range(pub_year_lims[0], pub_year_lims[1]))
    if (pub_year_range > 6) and (pub_year_range <= 12):
        pub_year_list = list(range(pub_year_lims[0], pub_year_lims[1]))[::2]
    if (pub_year_range > 12) and (pub_year_range <= 24):
        pub_year_list = list(range(pub_year_lims[0], pub_year_lims[1]))[::3]
    if (pub_year_range > 24) and (pub_year_range <= 36):
        pub_year_list = list(range(pub_year_lims[0], pub_year_lims[1]))[::4]
    if (pub_year_range > 36) and (pub_year_range <= 50):
        pub_year_list = list(range(pub_year_lims[0], pub_year_lims[1]))[::5]
    if (pub_year_range > 50):
        pub_year_list = list(range(pub_year_lims[0], pub_year_lims[1]))[::7]

    return pub_year_list

def determine_subplots(year_list):
    '''
    This function determines the necessary alignment of subplots for plotting the data in a dictionary of publication
    metric data. The routine simply takes the list of years to plot and determines the alignment of up to 
    4 subplot panels. 

        Inputs:
            year_list (list): the list of years to be plotted. This starts as the list of keys from the pubs_dict
                (output of get_publication_data), but is modified if a user specifies a different list of years
                and/or if the list is over 4 in length. 
        Outputs:
            axes (list): list of axes information for subplots. 

    '''

    aa = len(year_list)

    if aa <= 1:
        ax1 = plt.subplot2grid(shape=(4,4), loc=(0, 0), colspan=4, rowspan=4)
        axes = [ax1]
    elif aa == 2:
        ax1 = plt.subplot2grid(shape=(4,4), loc=(0, 0), colspan=2, rowspan=4)
        ax2 = plt.subplot2grid(shape=(4,4), loc=(0, 2), colspan=2, rowspan=4)
        axes = [ax1, ax2]
    elif aa == 3:
        ax1 = plt.subplot2grid(shape=(4,4), loc=(0, 0), rowspan=2, colspan=2 )
        ax2 = plt.subplot2grid(shape=(4,4), loc=(0, 2), rowspan=2, colspan=2 )
        ax3 = plt.subplot2grid(shape=(4,4), loc=(2, 1), rowspan=2, colspan=2 )
        axes = [ax1, ax2, ax3]
    elif aa >= 4:
        ax1 = plt.subplot2grid(shape=(4,4), loc=(0, 0), colspan=2, rowspan=2)
        ax2 = plt.subplot2grid(shape=(4,4), loc=(0, 2), colspan=2, rowspan=2)
        ax3 = plt.subplot2grid(shape=(4,4), loc=(2, 0), colspan=2, rowspan=2)
        ax4 = plt.subplot2grid(shape=(4,4), loc=(2, 2), colspan=2, rowspan=2)
        axes = [ax1, ax2, ax3, ax4]

    return axes


def Hirsch_panels_auto(pubs_dict, year_list=None, color_map='plasma'):
    '''
    This function takes the loaded data from pubs_dict and constructs a panel plot with up to 4 panels. If there are 
    more than 4 years in the pubs_dict, then it selects a sub-list of 4 years, including the latest one, and roughly 
    evenly spaced. If this is not desirable, a user can specify a list of years that they specifically would like to 
    populate the panels with. 

        Inputs: 
            pubs_dict (dictionary): This is the output of get_publication_data. Publication data can either be pulled 
                from an Excel workbook where the worksheets are citations and publicaitons from a given data pulled 
                from Google scholar (original method), or by using the auto_populate function (UNDER DEVELOPMENT)
                to create the necessary data structure for functions in this package. 
            year_list (keyword argument, list of 8 digit strings YYYYMMDD): User can supply a list of specific years 
                to populate the panels with. The list is automatically checked to make sure that the entries match
                the list of dictionary keys in pubs_dict. 
            color_map (string, python matplotlib colormaps): default: plasma. User can change color map if desired.
    
    '''

    #Check whether a list is given:
    keys_list = list(pubs_dict.keys())
    debug('Years from the pubs_dict are: ', keys_list)
    if year_list:
        good_list = [snap for snap in year_list if snap in keys_list]
        debug('Using ', year_list, ' to search for compatible years in ', keys_list)
        message0 = ['Year list is specified, pared down requested keys of pubs_dict to: ', good_list]
        if len(good_list) < len(year_list):
            message1 = ['Only found: ', good_list, ' in the publications data years uploaded.']
        else:
            message1 = 'Specified list matches publications data years.'
    else:
        good_list = keys_list
        message0 = 'Working with list of years in original dataset...'
        message1 = ''

    #If the list is longer than 4, pare list to 4:
    if len(good_list) > 4:
        ind = int(np.ceil(len(good_list)/4))
        good_list = good_list[::-ind][::-1]
        message2 = ['List of years shortened to 4: ', good_list, ' to fit graph. Please specify 4 specific years as "year_list" if you wish to plot different years than this selection.']
    else:
        message2 = ''

    print(message0, '\n', message1, '\n', message2)

    #Configure the axes and limits:
    fig = plt.figure()
    fig.set_figheight(6)
    fig.set_figwidth(6)
    axes = determine_subplots(good_list)
    good_dict = {key:pubs_dict[key] for key in good_list}
    debug(good_dict.keys())
    lims_dict, cbar_lims = limits_search(good_list, good_dict)
    xlimits = lims_dict['x']
    ylimits = lims_dict['y']
    pub_year_list = pub_year_colorbar_ticks(cbar_lims)

    #Now plot the years in the list:
    for j, snap in enumerate(good_dict.keys()):
        debug(j, snap)
        h, hirsch = plot_Hirsch(pubs_dict, axes[j], snap, pub_year_limits(pubs_dict, good_list), cmap=color_map)
        axes[j].set_ylim(ylimits)
        axes[j].set_xlim(xlimits)
        axes[j].text(0.3*max(xlimits), 0.75*max(ylimits),'H-index = '+str(h)+',\n ', fontdict=h_index_annotation_dict)
        axes[j].text(0.3*max(xlimits), 0.65*max(ylimits), snap[4:6]+'/'+snap[6::]+'/'+snap[:4], fontdict=date_annotation_dict)
    plt.tight_layout()  #Must do tightlayout prior to fitting big axes and color bar, or else the color bar prints over axes.

    #Add big bounding axis for a single set of y- and x-labels:
    big_ax = fig.add_subplot(111, frameon=False)
    plt.tick_params(labelcolor='none', which='both', top=False, bottom=False, left=False, right=False)
    big_ax.set_xlabel(xlabel='Publication rank, descending citations', fontdict=axis_label_dict)
    big_ax.set_ylabel(ylabel='Citations', fontdict=axis_label_dict)

    cbar = fig.colorbar(hirsch, ax=axes, shrink=0.95)
    year_list = [int(entry[:4]) for entry in good_list]
    cbar.set_ticks(pub_year_list)
    cbar.ax.set_ylabel(ylabel='Year published', fontdict=axis_label_dict)
    fig.patch.set_facecolor('white')  





def single_Hirsch_trim(fig, axs, hirsch_plot, year, h):
    '''
    This routine sets axis labels, color bar, color bar labels, and annotations for a single 
    Hirsch plot. This is separated from the function plot_Hirsch because that function plots
    only bare-bones plots for the double and quad plots that are available. Formatting for
    those plots is found in double_Hirsch_trim and quad_Hirsch_trim, respectively. 

    Inputs:
        fig: (matplotlib figure handle) figure handle for the figure that you are working with
        axis: (matplotlib axes handle) axes handle for the figure axes you are working with
        hirsch_plot: (matplotlib axes handle): axes handle for the plotted Hirsch plot
        year: (integer): Year of snapshot, taken as the first four digits of the snapshot
            string from the excel workbook, specified in the wrapper call. 
        h: (integer): The h-index calculated from the plotting routine, passed through
    '''

    fig.patch.set_facecolor('white')
    axs.set(xlabel='Rank (Descending order of citations)', ylabel='Citations')
    axs.xaxis.get_label().set_fontsize(16)
    axs.yaxis.get_label().set_fontsize(16)
    axs.xaxis.get_label().set_fontname('Arial')
    axs.yaxis.get_label().set_fontname('Arial')
    ylimits = axs.get_ylim()
    xlimits = axs.get_xlim()
    axs.text(0.5*max(xlimits), 0.75*max(ylimits),'H-index = '+str(h)+',\n ', fontdict=h_index_annotation_dict)
    axs.text(0.5*max(xlimits), 0.65*max(ylimits), year[4:6]+'/'+year[6::]+'/'+year[:4], fontdict=date_annotation_dict)    
    cbar = fig.colorbar(hirsch_plot, shrink=0.95)
    cbar.ax.set_ylabel(ylabel='Year published', fontdict=axis_label_dict)
    


def quad_Hirsch_trim(fig, axs, pubs_dict, hirsch_plot, year, h, year_list):
    '''
    This routine sets axis labels, color bar, color bar labels, and annotations for a quad panel 
    Hirsch plot. This is separated from the function plot_Hirsch because that function plots
    only bare-bones plots for the double and quad plots that are available. Formatting for
    those plots is found in double_Hirsch_trim and quad_Hirsch_trim, respectively. 

    Inputs:
        fig: (matplotlib figure handle) figure handle for the figure that you are working with
        axis: (matplotlib axes handle) axes handle for the figure axes you are working with
        hirsch_plot: (matplotlib axes handle): axes handle for the plotted Hirsch plot
        year: (integer): Year of snapshot, taken as the first four digits of the snapshot
            string from the excel workbook, specified in the wrapper call. 
        h: (integer): The h-index calculated from the plotting routine, passed through
        pubs_dict (dictionary): data from input spreadsheet
    '''

    limits = adjust_subplot_axes(axs, axis='both')
    pub_year_lims = pub_year_limits(pubs_dict, year_list)
    pub_year_range = pub_year_lims[1] - pub_year_lims[0]
    #Decide how may colorbar ticks to create by determining the time between limits.
    if pub_year_range <= 6:
        pub_year_list = list(range(pub_year_lims[0], pub_year_lims[1]))
    if (pub_year_range > 6) and (pub_year_range <= 12):
        pub_year_list = list(range(pub_year_lims[0], pub_year_lims[1]))[::2]
    if (pub_year_range > 12) and (pub_year_range <= 24):
        pub_year_list = list(range(pub_year_lims[0], pub_year_lims[1]))[::3]
    if (pub_year_range > 24) and (pub_year_range <= 36):
        pub_year_list = list(range(pub_year_lims[0], pub_year_lims[1]))[::4]
    if (pub_year_range > 36) and (pub_year_range <= 50):
        pub_year_list = list(range(pub_year_lims[0], pub_year_lims[1]))[::5]
    if (pub_year_range > 50):
        pub_year_list = list(range(pub_year_lims[0], pub_year_lims[1]))[::7]
    

    rangex = max(limits['x']) - min(limits['x'])
    for ind, axes in enumerate(axs.flatten()):
        axes.text(abs(0.17*rangex+min(limits['x'])), 0.85*max(limits['y']), 'H-index = '+str(h[ind])+',', fontdict=h_index_annotation_dict)
        axes.text(abs(0.17*rangex+min(limits['x'])), 0.7*max(limits['y']), year[ind][4:6]+'/'+year[ind][6::]+'/'+year[ind][:4], fontdict=date_annotation_dict)
        #Tick mark labels
        if ind < 2:
            axes.set_xticklabels([''])
        if ind % 2 != 0:
            axes.set_yticklabels([''])
    
    #Add big bounding axis for a single set of y- and x-labels:

    big_ax = fig.add_subplot(111, frameon=False)
    plt.tick_params(labelcolor='none', which='both', top=False, bottom=False, left=False, right=False)
    big_ax.set_xlabel(xlabel='Publication rank, descending citations', fontdict=axis_label_dict)
    big_ax.set_ylabel(ylabel='Citations', fontdict=axis_label_dict)

    cbar = fig.colorbar(hirsch_plot, ax=axs.ravel().tolist(), shrink=0.95)
    year_list = [int(entry[:4]) for entry in year]
    cbar.set_ticks(pub_year_list)
    cbar.ax.set_ylabel(ylabel='Year published', fontdict=axis_label_dict)
    fig.patch.set_facecolor('white')



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

    if isinstance(axes,np.ndarray):
        debug('Changing axes array into a list of axes.')
        axes = axes.flatten()

    for ax in axes:
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
            for lims in axes:
                lims.set_xlim(v)
        if k == 'y':
            for lims in axes:
                lims.set_ylim(v)
    
    return lims_dict

def h_index_panels(pubs_dict, snapshots_list, color_map='inferno'):
    '''
    Main wrapper function that the end user calls. This function takes user inputs central 
    to desired output - which years to plot, what font styles to use, and what color map.
    The function then decides how many axes to create in the figure, creates the figure and
    and the axes, plots the data in each axes, resizes the axes and adjusts the colorbar, and 
    informs the user of its choices with print commands.

    Inputs:
        snapshots_list: (list) a list containing at least one datecode lalbel from the excel 
            spreadsheet workbook. Function uses the size of this list to determine how 
            many axes to create (1, 2, or 4) and decides which snapshots to plot if the list
            contains a different number than 1, 2, or 4 snapshsot datecodes.
        color_map (string): a python color map for plots

    Outputs:
        fig: (pyplot figure handle): the figure handle in which all axes are plotted
        axs: (pyplot axes handles): the axes handles for the panel axes
    '''

    #Check if listed snapshots are in the keys of the pubs_dict; only work with those which are.
    keys_list = pubs_dict.keys()
    good_list = [snap for snap in snapshots_list if snap in keys_list]
    debug('Good List = ', good_list)
    cbar_limits = pub_year_limits(pubs_dict, good_list)
    
    #Plot bubble plots and print information messages depending on the length of snapshots_list
    if len(good_list) == 1:
        print('Plotting a single h-index bubble plot...')
        print('Compatible snapshots: ', good_list)
        #Create figure and axes for plot:
        fig, axs = plt.subplots(nrows=1, ncols=1)
        h, hirsch_plot = plot_Hirsch(pubs_dict, axs, snapshots_list[0], cbar_limits, cmap=color_map)
        single_Hirsch_trim(fig, axs, hirsch_plot, snapshots_list[0], h)

    if len(good_list) > 1:
        print('Attempting to plot 4-panel h-index evolution bubble plot...')
        if len(good_list) > 4:
            print('Detected more than 4 snapshot years in your list. Plotting the first four...')
            snaps = good_list[:4]
            print('Compatible snapshots: ', snaps)
            fig, axs, h = create_4panel_plot_trim(snaps, pubs_dict, snapshots_list, cbar_limits, color_map)
        if len(good_list) < 4:
            print('Detected fewer than 4 snapshot years in your snapshot list; plotting ONLY the first one...')
            print('Compatible snapshots: ', good_list)
            fig, axs = plt.subplots(nrows=1, ncols=1)
            h, hirsch_plot = plot_Hirsch(pubs_dict, axs, snapshots_list[0], cbar_limits, cmap=color_map)
            single_Hirsch_trim(fig, axs, hirsch_plot, snapshots_list[0], h)
        if len(good_list) == 4: #When there are 4 entries in snapshot list...
            print('Exactly 4 snapshots in list, plotting 4-panel plot.')
            print('Compatible snapshots: ', good_list)
            snaps = good_list
            fig, axs, h = create_4panel_plot_trim(snaps, pubs_dict, snapshots_list, cbar_limits, color_map)
    if len(good_list) == 0:
        print('List of citations snapshots is empty! Please fill the list, checking for transcription errors, and rerun code!')

    return fig, axs, h

def create_4panel_plot_trim(snaps, pubs_dict, year_list, cbar_limits, color_map):
    fig, axs = plt.subplots(nrows=2, ncols=2)
    h, hirsch_plot = [], []
    for ind, snap in enumerate(snaps):
        h_temp, hirsch_plot_temp = plot_Hirsch(pubs_dict, fig, axs.flatten()[ind], snap, cbar_limits, cmap=color_map)
        h.append(h_temp)
        hirsch_plot.append(hirsch_plot_temp)
    quad_Hirsch_trim(fig, axs, pubs_dict, hirsch_plot_temp, snaps, h, year_list)
    return fig, axs, h

def pub_year_limits(pubs_dict, year_list):
    '''
    Finds maximum and minimum years of publication to set the limits of color bars in multi-panel
    plots.

        Inputs: 
            pubs_dict (dictionary): dicionary of data input worksheet (as dataframes) from loading
                excel data into routine. Keys are date codes (YYYYMMDD) and values are dataframes.
        Outputs:
            pub_year_limits (tuple): min and max years of publications in the pubs_dict. Uused to 
                establsh the colorbar range and ticks in multipanel plots.
    '''
    new_dict = {}
    for year in year_list:
        if year in pubs_dict.keys():
            new_dict |= {year:pubs_dict[year]}

    min_years = []
    max_years = []
    for _, v in new_dict.items():
        min_year, max_year = min(v.Year), max(v.Year)
        min_years.append(min_year)
        max_years.append(max_year)

    pub_year_limits = (min(min_years), max(max_years))
    return pub_year_limits
