#!/usr/bin/python3

'''
Meta file for analysis of glycerol data
from Clark. Reuses generalized fns from
meta.py.

Jordan Dehmel, 2023
jdehmel@outlook.com
'''

import os
import re
import numpy as np
import pandas as pd
from typing import *
from matplotlib import pyplot as plt

import name_fixer
import filterer
import reverser

'''
Sections:

120 vs 240 um
Bottom Up vs Top Down
8, 12, 16, 20 v
SUBSECTION LABELS CHANGE BY SECTION

The files loaded here are ALREADY FILTERED
We just want to perform more analysis on
them.
'''

file_location: str = '/home/jorb/data_graphs'

# These filters are arranged in hierarchical order
main_folder_filter: str = ''

size_filters: [str] = ['120[_ ]?um', '240[_ ]?um']
directional_filters: [str] = ['[Tt]op[_ ]?[Dd]own', '[Bb]ottom[_ ]?[Uu]p']

voltage_filters: [str] = ['8[_ ][vV]', '12[_ ][vV]', '16[_ ][vV]', '20[_ ][vV]']
z_position_filters: [str] = ['8940', '8960', '8965', '8990', '8980',
                             '8985', '9010', '9015', '9035', '9040',
                             '9060', '9080', '9090', '9115', '9140',
                             '9197', '9255', '9280', '9305', '9240',
                             '9265', '9290', '9315', '9340', '9180',
                             '9205', '9230', '9255', '9280',
                             'top-100', 'top-25', 'top-50', 'top-75', 'top-97', 'top_',
                             'bot+25', 'bot+50', 'bot_']

# This string must be in the filename in order to load it
final_file_qualifier: str = 'track_data_summary.csv'


# Loads a list of lists of filters, and creates permutations of them.
# Returns a 'file tree' (recursive dictionary mapping filter lines to file lists)
def load_files_from_filter_hierarchy(hierarchy: [[str]], current_filters: [str] = []) -> Union[dict, List[pd.DataFrame]]:
    out: dict = {}

    if len(hierarchy) == 0:
        # Recursive base case
        print('Arrived at base case', current_filters)

        name_array: [str] = name_fixer.find_all(current_filters[0])

        for filter in current_filters[1:]:
            temp: [str] = name_fixer.find_all(filter)

            name_array = [name for name in name_array if name in temp]

            if len(name_array) == 0:
                break

        name_array = [name for name in name_array if re.search(final_file_qualifier, name) is not None]

        file_array: [pd.DataFrame] = [pd.read_csv(name) for name in name_array]

        return file_array

    else:
        for filter in hierarchy[0]:
            result = load_files_from_filter_hierarchy(hierarchy[1:], current_filters + [filter])
            
            if type(result) != list or len(result) != 0:
                out[filter]= result
        
        return out


def print_names(what, tab: int = 1) -> None:
    if type(what) == dict:
        for item in what:
            print('|' * tab + str(item))
            print_names(what[item], tab + 1)
    else:
        print('|' * tab + str(type(what)), len(what))

    return


# Plots and graphs sls from a file tree,
# as established by the above functions
def plot_sls_from_file_tree(tree) -> None:
    pass


def do_set_of_files(files: [pd.DataFrame],
                    real_names: [str],
                    output_prefix: str,
                    do_3d_graph: bool = False,
                    do_2d_graphs: bool = False,
                    do_2d_combined_graph: bool = False,
                    title: str = 'title') -> None:
    # A) Find average straight line speed across all frequencies by voltage
    array: [[float]] = [[0.0, 0.0] for _ in real_names]

    for i, file in enumerate(files):
        array[i][0] = np.mean(file['MEAN_STRAIGHT_LINE_SPEED'])
        array[i][1] = np.std(file['MEAN_STRAIGHT_LINE_SPEED'])

    # Build output csv file from A
    average_speeds_df: pd.DataFrame = pd.DataFrame(array,
                                                   index=real_names,
                                                   columns=['MEAN_STRAIGHT_LINE_SPEED', 'MSLS_STD'])

    # Save output csv file from A
    average_speeds_df.to_csv(output_prefix + 'sls_by_voltage.csv')

    # B) Find straight line speeds across a GIVEN frequency by voltage
    # For each frequency

    # Build output csv files from B

    # Save output csv files from B

    if do_2d_graphs:
        # Build output graphs from A
        filterer.graph_column_with_bars(average_speeds_df,
                                        average_speeds_df,
                                        'MEAN_STRAIGHT_LINE_SPEED',
                                        'MSLS_STD',
                                        output_prefix + 'sls_by_voltage.png',
                                        override_ticks=['5v', '10v', '15v'])

        # Build output graphs from B
        # Save output graphs from B

    # Do 3d graph if wanted (because I think it's cool)
    if do_3d_graph:
        plt.rc('font', size=6)

        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        ax.set_title(title)

        colors: [str] = ['r', 'g', 'b', 'y']
        voltages: [float] = [5, 10, 15]

        '''
        Z = voltages
        X = frequency
        Y = mean straight line speed
        '''
        for i in range(len(files)):
            xs: [str] = [str(row[1][0]) for row in files[i].iterrows()]
            ys: [float] = [data for data in files[i]
                           ['MEAN_STRAIGHT_LINE_SPEED'].astype(float)]

            cs: str = colors[i % len(colors)]

            ax.bar(xs,
                   ys,
                   zs=[voltages[i % len(voltages)] for _ in cs],
                   zdir='y',
                   color=cs,
                   alpha=0.8)

        ax.set_xlabel('Applied Frequency (Hertz)')
        ax.set_zlabel('Mean Straight Line Speed (Pixels / Frame)')
        ax.set_ylabel('Applied Voltage (Volts)')

        plt.show()

    if do_2d_combined_graph:
        voltages: [float] = [5, 10, 15]

        rows: [[str]] = []
        data: [[float]] = []

        for i in range(len(files)):
            rows.append([str(row[1][0]) for row in files[i].iterrows()])
            data.append([data for data in files[i]
                         ['MEAN_STRAIGHT_LINE_SPEED'].astype(float)])

        axis_labels: (str) = ('Applied Frequency (Hertz)',
                              'Mean Straight Line Speed (Pixels / Frame)')

        save_paths: [str] = [filterer.secondary_save_path +
                             output_prefix + 'combined_voltages.png',
                             '/home/jorb/Programs/physicsScripts/' +
                             output_prefix + 'combined_voltages.png']

        reverser.graph_multiple_relative(
            data, [10000.0 for _ in voltages], rows, save_paths, axis_labels, voltages)

    return


if __name__ == '__main__':
    os.chdir(file_location)
    hierarchy: [[str]] = [size_filters, directional_filters, voltage_filters]

    files = load_files_from_filter_hierarchy(hierarchy)
    
    print_names(files)
