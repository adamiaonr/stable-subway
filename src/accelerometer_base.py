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

def plot_accelerometer_session(data, output_dir):

    # 4 stacked subplots (4 lines, 1 column), one line 
    # per axix (xx, yy and zz) + total
    fig = plt.figure(figsize = (12, 12))
    # codes for subplots (labels, colors, etc.)
    subplot_codes = {411 : 'acc-xx:red', 412 : 'acc-yy:green', 413 : 'acc-zz:blue', 414 : 'acc-total:black'}
    # event codes
    event_codes = {'s' : 'stop:blue:--', 'd' : 'depart:green:--', 'x' : 'steep accel.:red:--', 'e' : 'enter:black:-.', 'l' : 'leave:black:-.'}

    # FIXME : assume only 1 section for now
    for session_id in data:

        # extract the rows with events on them (dropping all lines with 'NaN' values on them)
        events = data[session_id].dropna()
        # determine the start of the subway ride (event-type 's', event-descr 'e')
        start_timestamp = events.iloc[0]['time'] - 10
        end_timestamp = events.iloc[-1]['time'] + 10

        # truncate data for values after the start of the subway ride
        subway_ride_data = data[session_id][ (data[session_id]['time'] >= start_timestamp) & (data[session_id]['time'] <= end_timestamp) ]
        # change 'time' column to seconds after start of ride
        subway_ride_data['time'] = (subway_ride_data['time'] - start_timestamp)
        events['time'] = (events['time'] - start_timestamp)

        for code in subplot_codes:

            ax = fig.add_subplot(code)
            # if 1st subplot, add title
            if (code == 411):
                ax.set_title("IPO > Trindade")

            ax.xaxis.grid(False)
            ax.yaxis.grid(True)

            ax.plot(subway_ride_data['time'], subway_ride_data[subplot_codes[code].split(":")[0]], color = subplot_codes[code].split(":")[1])
            ax.legend(fontsize = 10, ncol = 1, loc = 'upper left')

            y_min = math.floor(min(subway_ride_data[subplot_codes[code].split(":")[0]])) 
            y_max = math.ceil(max(subway_ride_data[subplot_codes[code].split(":")[0]]))

            ax.set_ylim(math.floor(min(subway_ride_data[subplot_codes[code].split(":")[0]])), math.ceil(max(subway_ride_data[subplot_codes[code].split(":")[0]])))
            ax.set_yticks( np.arange(y_min, y_max + 1, step = 1.0) )

            ax.set_ylabel("accel. (m^2 / s)")

            # print event vertical lines
            added_labels = []
            for index, event in events.iterrows():

                label = event_codes[event['event-descr']].split(":")[0]
                if label not in added_labels:
                    ax.axvline(event['time'], label = label, color = event_codes[event['event-descr']].split(":")[1], linestyle = event_codes[event['event-descr']].split(":")[2])
                    added_labels.append(label)
                else:
                    ax.axvline(event['time'], color = event_codes[event['event-descr']].split(":")[1], linestyle = event_codes[event['event-descr']].split(":")[2])

            ax.legend(fontsize = 10, ncol = 6, loc = 'upper center')            

        ax.set_xlabel("subway trip duration")

    # accelerometer_components = ['xx', 'yy', 'zz', 'avg. total']
    # accelerometer_components_colors = ['red', 'green', 'blue', 'black']

    plt.savefig(os.path.join(output_dir, "accelerometer-session.pdf"), bbox_inches='tight', format = 'pdf')


