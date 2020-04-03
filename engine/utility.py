import numpy as np
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models import Band, Range1d
from bokeh.layouts import gridplot
from flask import flash, redirect
from bokeh.models.widgets import Panel, Tabs
import os

plot_height, plot_width = 250, 600


def daily_infection_rate(N, Ni, t):

    return 100 - 100 * ((N - Ni) / N) ** (1 / t)


def save_survey(survey):

    # Convert answers to pandas dataframe
    df = pd.DataFrame(survey)

    # Survey is not filled
    if (not survey['Appearance'] and not survey['Usability'] and
       not survey['Usefulness'] and not survey['Comment']):

        # Save the info in a parameter
        filled = False

    # Servey is filled
    else:

        # Save the info in a parameter
        filled = True

    if not os.path.isfile('pub/survey.csv'):

        # if file does not exist write header
        df.to_csv('pub/survey.csv', header='column_names')

    else:

        # else it exists so append without writing the header
        df.to_csv('pub/survey.csv', mode='a', header=False)

    return filled


def update_par(session):

    try:
        # Convert list to string
        DOS = '-'.join([str(elem)for elem in session['DO']])
        IRS = '-'.join([str(elem)for elem in session['IR']])

        # Convert None to string
        if session['optional1'] is None:
            OPT = ['N/A', 'N/A']
        else:
            OPT = [session['optional1'], session['optional2']]

        # Create a dictionary based on the parameters
        d = {'Date': [session['date']],
             'Type': [session['dep_type']],
             'TnS': [session['parameters'][0]],
             'LoS': [session['parameters'][1]],
             'NoA': [session['parameters'][2]],
             'DiR': [session['parameters'][3]],
             'CA': OPT[0],
             'CsN': OPT[1],
             'IrW': [IRS],
             'DoS': [DOS]}

        # Convert the dict to dataframe
        df = pd.DataFrame(d)

        if not os.path.isfile('pub/shared_par.csv'):

            # if file does not exist write header
            df.to_csv('pub/shared_par.csv', header='column_names')

        else:

            # else it exists so append without writing the header
            df.to_csv('pub/shared_par.csv', mode='a', header=False)

        # Sucessfully saved
        save = True

    except ValueError:

        # Saving failed
        save = False

    return save


def err(url, message):

    # Error message to the front end
    flash(message)

    # Redirect to the same page if type conversion fails
    return redirect(url)


def parameter_matrix(nG):

    # Infection Rate at Work for each area, parameter names
    IRL = np.array(['IR' + str(x) for x in range(1, nG + 1)])

    # Days Off per Shift for each area, parameter names
    DOL = np.array(['DO' + str(x) for x in range(1, nG + 1)])

    # Create labesl for ares
    LAB = np.array(['Area ' + str(x) + ': ' for x in range(1, nG + 1)])

    # Create default parameter values
    IRD = np.array([7] + [2 for x in range(nG - 1)])
    DOD = np.array([0] + [2 for x in range(nG - 1)])

    # 'n' by 4 matrix of parameters IRL and DOL for the frontend
    number_of_rows = int(len(IRL) // 4)
    if len(IRL) % 4 != 0:
        number_of_rows += 1

    # Shape the parameters to matrix form
    DOL.resize(number_of_rows, 4)
    IRL.resize(number_of_rows, 4)
    LAB.resize(number_of_rows, 4)
    IRD.resize(number_of_rows, 4)
    DOD.resize(number_of_rows, 4)

    # Save dimensions of matrix
    dim = [len(IRL[0, :]), len(IRL[:, 0])]

    # Create a dictionery for the properties
    return {'DOL': DOL, 'IRL': IRL,
            'DOD': DOD, 'IRD': IRD,
            'Serial': LAB, 'dim': dim}


def area_difference_plot(dm):

    # Separate the the datasets, with and without rearrangement
    dataset1 = dm[0]
    dataset2 = dm[1]

    # Sotre subplots
    subplot = []

    # Colour scale
    c = ["#0066b3", "#117733", "#999933", "#8B0000"]

    for i in range(len(dataset1)):

        # Calculate the difference WITHOUT - WITH REARRANGEMENT

        x = dataset1[i]["x"]
        total_mean = dataset1[i]["y"] - dataset2[i]["y"]
        coi_l = dataset1[i]["y_low"] - dataset2[i]["y_low"]
        coi_h = dataset1[i]["y_high"] - dataset2[i]["y_high"]

        # Dataframe to store the data
        dframe = pd.DataFrame({"x": x, "y": total_mean,
                               "y_low": coi_l, "y_high": coi_h})

        # Convert the dataframe to bokeh source
        d1 = ColumnDataSource(dframe)

        # Create canveas
        ta = figure(plot_height=plot_height, plot_width=plot_width)

        # Difference plot
        line1 = ta.line(x="x",
                        y="y",
                        source=d1,
                        line_color=c[i],
                        line_alpha=0.75,
                        line_width=1.5,
                        legend_label='Available to work')

        # Set fig title
        ta.title.text = 'Area ' + str(i + 1)

        # Setup the y labels
        ta.yaxis.axis_label = 'Staff Difference'

        # Setup the x labels
        ta.xaxis.axis_label = 'Days'

        # Transparent background
        ta.border_fill_color = None
        ta.background_fill_color = None

        # Remove grid
        ta.xgrid.grid_line_color = None
        ta.ygrid.grid_line_color = None

        # Legend setup
        ta.legend.background_fill_alpha = 0.0
        ta.legend.border_line_alpha = 0.0

        # Ad panel to sublot
        subplot.append(ta)

    grid = gridplot(subplot, ncols=1,
                    plot_width=plot_width,
                    plot_height=plot_height)

    return grid


def plot_total_col(day, total_col_plot, ca, cn, panel, diff):

    # Panel titles
    tab_title = ['Without Staff Rearrangement', 'After Staff Rearrangement']

    # Store the panels in a list
    panels = []

    # Difference matrix
    dm = []

    for j in range(2):

        if panel is False:

            # Define x-axis
            x = day[0]

            # y-axis, all group, matrix 2D
            y_all_group = total_col_plot

        else:

            # x-axis, array 1D
            x = day[j][0]

            # y-axis, all group, matrix 2D
            y_all_group = total_col_plot[j]

        # Reorganise the diemension of 3d array
        y_all_group = np.array(y_all_group).transpose(1, 0, 2)

        # Collect al subplots
        subplot = []

        # Save the dta fro the difference plot
        diff = []

        # Colour scale
        c = ["#0066b3", "#117733", "#999933", "#8B0000"]

        # Iterate over y-axis
        for i, group in enumerate(y_all_group):

            # Set a colour for the subplot
            colour = c[i % 4]

            # Calculate mean and std
            mean, p5, p95 = stats(group)

            # Create COI
            coi_l = p5
            coi_h = p95

            # MAximum Staff in group
            #w_max = int(mean[0])

            # Set limits
            #coi_l[coi_l < 0] = 0
            #coi_h[coi_h > w_max] = w_max

            # Create figure canvas
            fig = figure(plot_height=plot_height, plot_width=plot_width)

            # Create Pandas dataframe
            df = pd.DataFrame({"x": x, "y": mean,
                               "y_low": coi_l, "y_high": coi_h})

            # Add the subplot's data to difference array
            diff.append(df)

            # Replace zeros with NaN and drop them
            df = df.replace(0, np.nan).dropna()

            # Create Data Source for plotting the data
            d1 = ColumnDataSource(df)

            # First plot
            line1 = fig.line(x="x",
                             y="y",
                             source=d1,
                             line_color=colour,
                             line_alpha=0.75,
                             line_width=1.5)

            band1 = Band(base='x', lower='y_low', upper='y_high', source=d1,
                         level='underlay', fill_alpha=0.25,
                         line_width=1, line_color=colour,
                         fill_color=colour)

            # Create custom hover and add the hover to the plot
            hov1 = [('Days', '@x'), ('Available to work (avg)', '@y{int}'),
                    ('Available to work (min)', '@y_low{int}'),
                    ('Available to work (max)', '@y_high{int}')]

            # Create custom hover and add the hover to the plot
            fig.add_tools(HoverTool(renderers=[line1], tooltips=hov1))

            # Set fig title
            fig.title.text = 'Area ' + str(i + 1)

            if ca is not False:

                if (i + 1) == int(ca):

                    # Set fig title
                    fig.title.text = 'Area ' + ca + ' (Critical Area)'

                    # Critical limit
                    fig.line(x=df['x'],
                             y=np.full(len(df['x']), int(cn)),
                             line_color='black',
                             line_alpha=0.5,
                             line_width=1,
                             legend_label='Critical value for Area ' + ca)

                    fig.legend.location = 'bottom_right'

                    fig.legend.background_fill_alpha = 0.0
                    fig.legend.border_line_alpha = 0.0

            # Setup the y labels
            fig.yaxis.axis_label = 'Total Number of Staff'

            # Setup the x labels
            fig.xaxis.axis_label = 'Days'

            # Transparent background
            fig.border_fill_color = None
            fig.background_fill_color = None

            # Remove grid
            fig.xgrid.grid_line_color = None
            fig.ygrid.grid_line_color = None

            # Setup range
            fig.x_range = Range1d(0, 180)
            fig.y_range = Range1d(int(df['y_low'].min()) - df['y_low'].min() * .1,
                                  int(df['y_high'].max()))

            # Add custom COI
            fig.add_layout(band1)

            # Append the figure with new subplot
            subplot.append(fig)

        # make a grid
        grid = gridplot(subplot, ncols=1,
                        plot_width=plot_width,
                        plot_height=plot_height)

        if panel is False:
            return components(grid)

        else:

            # Add the new panel to the final plot
            panels.append(Panel(child=grid, title=tab_title[j]))

            # Save the data for the difference plot
            dm.append(diff)

    if diff is True:

        # Call the function, plotting the difference between the datasets
        grid = area_difference_plot(dm)

        # Add the new panel to the final plot
        panels.append(Panel(child=grid, title='Difference'))

    return components(Tabs(tabs=panels))


def stats(data):

    return (np.mean(data, axis=0),
            np.percentile(data, 5, axis=0),
            np.percentile(data, 95, axis=0))


def total_diff_plot(diff):

    # Calculate the difference WITHOUT - WITH REARRANGEMENT
    x = diff[0]["x"]
    total_mean = diff[0]["y"] - diff[1]["y"]
    coi_l = diff[0]["y_low"] - diff[1]["y_low"]
    coi_h = diff[0]["y_high"] - diff[1]["y_high"]

    # Dataframe to store the data
    dframe = pd.DataFrame({"x": x, "y": total_mean,
                           "y_low": coi_l, "y_high": coi_h})

    # Convert the dataframe to bokeh source
    d1 = ColumnDataSource(dframe)

    # Create canveas

    ta = figure(plot_height=plot_height, plot_width=plot_width)

    # Difference plot
    line1 = ta.line(x="x",
                    y="y",
                    source=d1,
                    line_color="#0066b3",
                    line_alpha=0.75,
                    line_width=1.5,
                    legend_label='Available to work')

    # Setup the y labels
    ta.yaxis.axis_label = 'Staff Difference'

    # Setup the x labels
    ta.xaxis.axis_label = 'Days'

    # Transparent background
    ta.border_fill_color = None
    ta.background_fill_color = None

    # Remove grid
    ta.xgrid.grid_line_color = None
    ta.ygrid.grid_line_color = None

    # Legend setup
    ta.legend.background_fill_alpha = 0.0
    ta.legend.border_line_alpha = 0.0

    return ta


def plot_total(day, total, panel, diff):
    '''This function generates the results as a bokeh figure.

    Args:
        re (dict): Generated by the covid19 engine.

    Returns:
        str: Bokeh embedded Javascript for the frontend template.

    '''

    # Create figure canvas
    tabs = [figure(plot_height=plot_height, plot_width=plot_width),
            figure(plot_height=plot_height, plot_width=plot_width)]

    # Panel titles
    tab_title = ['Without Staff Rearrangement',
                 'After Staff Rearrangement']

    # Difference data
    diff = []

    # Store the panels in a list
    panels = []

    for i, ta in enumerate(tabs):

        # Create figure canvas

        if panel is False:

            # Calculate mean and std
            total_mean, p5, p95 = stats(total)

            # x-axis
            x = day[0]

        else:

            # Calculate mean and std
            total_mean, p5, p95 = stats(total[i])

            # x-axis
            x = day[i][0]

        # M ax worker number
        w_max = np.array(total).max()

        # Create COI
        coi_l = p5
        coi_h = p95

        # Set limits
        #coi_l[coi_l < 0] = 0
        #coi_h[coi_h > w_max] = w_max

        # Create a pandas dataframe
        dframe = pd.DataFrame({"x": x, "y": total_mean,
                               "y_low": coi_l, "y_high": coi_h})

        # Save the dataframe for difference plot
        diff.append(dframe)

        # Create Data Source for plotting the data
        d1 = ColumnDataSource(dframe)
        d2 = ColumnDataSource(pd.DataFrame({"x": x,
                                            "y": w_max - total_mean,
                                            "y_low": w_max - coi_l,
                                            "y_high": w_max - coi_h}))

        # First plot
        line1 = ta.line(x="x",
                        y="y",
                        source=d1,
                        line_color="#0066b3",
                        line_alpha=0.75,
                        line_width=1.5,
                        legend_label='Available to work')

        # 2nd plot
        line2 = ta.line(x="x",
                        y="y",
                        source=d2,
                        line_color="#117733",
                        line_alpha=0.75,
                        line_width=1.5,
                        legend_label='Unavailable to work')

        band1 = Band(base='x', lower='y_low', upper='y_high', source=d1,
                     level='underlay', fill_alpha=0.25,
                     line_width=1, line_color='#0066b3',
                     fill_color='#0066b3')

        band2 = Band(base='x', lower='y_low', upper='y_high', source=d2,
                     level='underlay', fill_alpha=0.25,
                     line_width=1, line_color='#117733',
                     fill_color='#117733')

        # Add custom COI
        ta.add_layout(band1)
        ta.add_layout(band2)

        # Create custom hover and add the hover to the plot
        hov1 = [('Days', '@x'), ('Available to work (avg)', '@y{int}'),
                ('Available to work (min)', '@y_low{int}'),
                ('Available to work (max)', '@y_high{int}')]

        hov2 = [('Days', '@x'), ('Unavailable to work (avg)', '@y{int}'),
                ('Unavailable to work (max)', '@y_low{int}'),
                ('Unavailable to work (min)', '@y_high{int}')]

        # Create custom hover and add the hover to the plot
        ta.add_tools(HoverTool(renderers=[line1], tooltips=hov1))
        ta.add_tools(HoverTool(renderers=[line2], tooltips=hov2))

        # Setup the y labels
        ta.yaxis.axis_label = 'Total Number of Staff'

        # Setup the x labels
        ta.xaxis.axis_label = 'Days'

        # Transparent background
        ta.border_fill_color = None
        ta.background_fill_color = None

        # Remove grid
        ta.xgrid.grid_line_color = None
        ta.ygrid.grid_line_color = None

        # Setup range
        ta.x_range = Range1d(0, 180)
        ta.y_range = Range1d(0, int(coi_h.max()))

        ta.legend.location = 'center_right'

        ta.legend.background_fill_alpha = 0.0
        ta.legend.border_line_alpha = 0.0

        if panel is False:
            return components(ta)

        else:
            panels.append(Panel(child=ta, title=tab_title[i]))

    if diff is True:

        # Create the difference
        ta = total_diff_plot(diff)

        # Append the difference plot
        panels.append(Panel(child=ta, title='Difference'))

    return components(Tabs(tabs=panels))
