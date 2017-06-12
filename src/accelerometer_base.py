import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os
import argparse
import sys
import glob
import math

from datetime import date
from datetime import datetime
from collections import defaultdict
from collections import OrderedDict

# custom imports
from plot_utils import *

matplotlib.rcParams.update({'font.size': 16})

def plot_acceleration_patterns(data, output_dir):

    for session_id in data:

        # 2 types of plots:
        #   - (fig1) stop and departure patterns, w/ acceleration for every stop and departure in 
        #     the session : 2 columns of 4 stacked time series
        #   - (fig2) cdf of times spent at stop

        # codes for subplots (labels, colors, etc.) for the 1st column 
        # (stop patterns). the 2nd column (departure patterns)
        subplot_codes = {421 : 'acc-xx:red', 423 : 'acc-yy:green', 425 : 'acc-zz:blue', 427 : 'acc-total:black'}
        # event codes
        event_codes = {'s' : 'stop:blue:--', 'd' : 'depart:green:--', 'x' : 'steep accel.:red:--', 'e' : 'enter:black:-.', 'l' : 'leave:black:-.'}

        # extract start and stop stations
        start_station = session_id.split("_")[1].replace("-", " ").upper()
        end_station = session_id.split("_")[2].replace("-", " ").upper()

        # extract the rows with events on them (dropping all lines with 'NaN' values on them)
        events = data[session_id].dropna()

        # determine the start of the subway ride (event-type 's', event-descr 'e')
        start_timestamp = events.iloc[0]['time'] - 2
        end_timestamp = events.iloc[-1]['time'] + 2
        # truncate data for values after the start of the subway ride
        subway_ride_data = data[session_id][ (data[session_id]['time'] >= start_timestamp) & (data[session_id]['time'] <= end_timestamp) ]
        # remove outliers (only consider values within +2 to -2 std dev)
        for code in subplot_codes:
            subway_ride_data = subway_ride_data[np.abs(subway_ride_data[subplot_codes[code].split(":")[0]] - subway_ride_data[subplot_codes[code].split(":")[0]].mean()) <= (3 * subway_ride_data[subplot_codes[code].split(":")[0]].std())]

        # fig1 : stop and acceleration patterns
        fig_1 = plt.figure(figsize = (12, 2 * 12))

        # set main title
        fig_1.suptitle(start_station + " > " + end_station)

        # draw 1 column at a time (first stop, then departure patterns)
        for i, pattern in {0 : 's:20:10', 1 : 'd:10:20'}.iteritems():

            pattern_type = pattern.split(":")[0]
            pattern_before  = int(pattern.split(":")[1])
            pattern_after   = int(pattern.split(":")[2])

            # subplot hashtable
            subplots = {}
            yy_min = {}
            yy_max = {}
            legends = []

            # draw all stop events on same graph
            for index, event in events[(events['event-descr'] == pattern_type)].iterrows():

                # get start and end timestamps for pattern
                event_tmstmp = event['time']

                # select the values within the appropriate timespan in xx and yy
                selection = subway_ride_data[(subway_ride_data['time'] >= (event_tmstmp - pattern_before)) & (subway_ride_data['time'] <= (event_tmstmp + pattern_after))]
                # adjust the timestamps in order to get a time range from 0 to 30s
                selection.loc[:, 'time'] = (selection['time'] - (event_tmstmp - pattern_before))

                # draw 4 stacked graphs, one for each acc axis
                for code in subplot_codes:
                    
                    if (code + i) not in subplots: 

                        subplots[code + i] = fig_1.add_subplot(code + i)
                        subplots[code + i].xaxis.grid(False)
                        subplots[code + i].yaxis.grid(True)

                        # add titles to columns
                        if (code + i) == 421:
                            subplots[code + i].set_title("Stop accel.")
                        elif (code + i) == 422:
                            subplots[code + i].set_title("Departure accel.")

                        # add x-axis label
                        subplots[code + i].set_xlabel("time")
                        # add y-axis label
                        subplots[code + i].set_ylabel("accel. (m / s^2)")

                        # plot a vertical line, indicating the event
                        label = event_codes[event['event-descr']].split(":")[0]
                        subplots[code + i].axvline(pattern_before, label = label, color = event_codes[event['event-descr']].split(":")[1], linestyle = event_codes[event['event-descr']].split(":")[2])

                    # keep track of yy_min
                    if (code + i) not in yy_min:
                        yy_min[code + i] = math.floor(min(selection[subplot_codes[code].split(":")[0]]))
                    else:

                        if math.floor(min(selection[subplot_codes[code].split(":")[0]])) < yy_min[code + i]:
                            yy_min[code + i] = math.floor(min(selection[subplot_codes[code].split(":")[0]]))

                    # and of yy_max
                    if (code + i) not in yy_max:
                        yy_max[code + i] = math.ceil(max(selection[subplot_codes[code].split(":")[0]])) - 0.25
                    else:

                        if math.ceil(max(selection[subplot_codes[code].split(":")[0]])) > yy_max[code + i]:
                            yy_max[code + i] = math.ceil(max(selection[subplot_codes[code].split(":")[0]])) - 0.25

                    subplots[code + i].set_ylim(yy_min[code + i], yy_max[code + i])
                    subplots[code + i].set_yticks( np.arange(yy_min[code + i], yy_max[code + i] + 0.25, step = 0.25) )
                        
                    subplots[code + i].plot(selection['time'], selection[subplot_codes[code].split(":")[0]], color = subplot_codes[code].split(":")[1])

                    if (code + i) not in legends:
                        subplots[code + i].legend(fontsize = 12, ncol = 1, loc = 'upper left')
                        legends.append(code + i)

        # tight layout often produces nice results
        # but requires the title to be spaced accordingly
        fig_1.tight_layout()
        fig_1.subplots_adjust(top = 0.95)

        plt.savefig(os.path.join(output_dir, "acceleration-patterns-" + session_id.split("_")[0] + ".pdf"), bbox_inches = 'tight', format = 'pdf')

def plot_accelerometer_session(data, output_dir):

    # codes for subplots (labels, colors, etc.)
    subplot_codes = {411 : 'acc-xx:red', 412 : 'acc-yy:green', 413 : 'acc-zz:blue', 414 : 'acc-total:black'}
    # event codes
    event_codes = {'s' : 'stop:blue:--', 'd' : 'depart:green:--', 'x' : 'steep accel.:red:--', 'e' : 'enter:black:-.', 'l' : 'leave:black:-.'}

    for session_id in data:

        # extract start and stop stations
        start_station = session_id.split("_")[1].replace("-", " ").upper()
        end_station = session_id.split("_")[2].replace("-", " ").upper()

        # 4 stacked subplots (4 lines, 1 column), one line 
        # per axix (xx, yy and zz) + total
        fig = plt.figure(figsize = (12, 12))

        # extract the rows with events on them (dropping all lines with 'NaN' values on them)
        events = data[session_id].dropna()
        # determine the start of the subway ride (event-type 's', event-descr 'e')
        start_timestamp = events.iloc[0]['time'] - 2
        end_timestamp = events.iloc[-1]['time'] + 2

        # truncate data for values after the start of the subway ride
        subway_ride_data = data[session_id][ (data[session_id]['time'] >= start_timestamp) & (data[session_id]['time'] <= end_timestamp) ]
        # remove outliers (only consider values within +2 to -2 std dev)
        for code in subplot_codes:
            subway_ride_data = subway_ride_data[np.abs(subway_ride_data[subplot_codes[code].split(":")[0]] - subway_ride_data[subplot_codes[code].split(":")[0]].mean()) <= (3 * subway_ride_data[subplot_codes[code].split(":")[0]].std())]

        # change 'time' column to seconds after start of ride
        subway_ride_data.loc[:, 'time'] = (subway_ride_data['time'] - start_timestamp)
        events.loc[:, 'time'] = (events['time'] - start_timestamp)

        for code in subplot_codes:

            ax = fig.add_subplot(code)
            # if 1st subplot, add title
            if (code == 411):
                ax.set_title(start_station + " > " + end_station)

            ax.xaxis.grid(False)
            ax.yaxis.grid(True)

            ax.plot(subway_ride_data['time'], subway_ride_data[subplot_codes[code].split(":")[0]], color = subplot_codes[code].split(":")[1])

            y_min = math.floor(min(subway_ride_data[subplot_codes[code].split(":")[0]]))
            y_max = math.ceil(max(subway_ride_data[subplot_codes[code].split(":")[0]]))

            ax.set_ylim(math.floor(min(subway_ride_data[subplot_codes[code].split(":")[0]])), math.ceil(max(subway_ride_data[subplot_codes[code].split(":")[0]])) + 0.5)
            ax.set_yticks( np.arange(y_min, y_max + 1, step = 1.0) )

            ax.set_ylabel("accel. (m / s^2)")

            # print event vertical lines
            added_labels = []
            for index, event in events.iterrows():

                label = event_codes[event['event-descr']].split(":")[0]
                if label not in added_labels:
                    ax.axvline(event['time'], label = label, color = event_codes[event['event-descr']].split(":")[1], linestyle = event_codes[event['event-descr']].split(":")[2])
                    added_labels.append(label)
                else:
                    ax.axvline(event['time'], color = event_codes[event['event-descr']].split(":")[1], linestyle = event_codes[event['event-descr']].split(":")[2])

            ax.legend(fontsize = 12, ncol = 6, loc = 'upper center')            

        ax.set_xlabel("subway trip duration")

        # accelerometer_components = ['xx', 'yy', 'zz', 'avg. total']
        # accelerometer_components_colors = ['red', 'green', 'blue', 'black']

        plt.savefig(os.path.join(output_dir, "accelerometer-session-" + session_id.split("_")[0] + ".pdf"), bbox_inches='tight', format = 'pdf')


