#!/usr/bin/python3

import pandas as pd
from numpy import zeros
import matplotlib.pyplot as plt
from os import *
from sys import *
from time import time


# What columns to keep from the .csv files
col_names: [str] = ['TRACK_DISPLACEMENT', 'TRACK_MEAN_SPEED',
                    'TRACK_MEDIAN_SPEED', 'TRACK_STD_SPEED',
                    'TOTAL_DISTANCE_TRAVELED', 'MEAN_STRAIGHT_LINE_SPEED',
                    'LINEARITY_OF_FORWARD_PROGRESSION']

# Which frequencies to scan
frequencies: [str] = ['0', '0.8', '1', '10',
                      '25', '50', '75', '100',
                      '150', '200']

# The folder to operate on. Will be replaced by the cwd
folder: str = ''

# The suffix to follow X-khz
suffix: str = 'trackexport.csv'

do_speed_thresh: bool = True
do_displacement_thresh: bool = True


# Analyze a file with a given name, and return the results
def do_file(name: str, displacement_threshold: float = 0.0, speed_threshold: float = 0.0) -> [float]:
    try:
        # Load file
        csv = pd.read_csv(name + suffix)
    except:
        print('Failed to open', name + suffix)
        return [-1 for _ in col_names]

    print('Using displacement threshold', displacement_threshold,
          'speed threshold', speed_threshold)

    # Drop useless data (columns)
    names_to_drop: [str] = []
    for column_name in csv.columns:
        if column_name not in col_names:
            names_to_drop.append(column_name)

    csv.drop(axis=1, inplace=True, labels=names_to_drop)

    # Drop useless data (rows)
    csv.drop(axis=0, inplace=True, labels=[0, 1, 2])

    initial_num_rows: int = len(csv)

    # Do thresholding here
    if do_speed_thresh or do_displacement_thresh:
        for row in csv.iterrows():
            if do_speed_thresh:
                # Must meet mean speed threshold
                if float(row[1]['TRACK_MEAN_SPEED']) < speed_threshold:
                    csv.drop(axis=0, inplace=True, labels=[row[0]])
                    continue

            if do_displacement_thresh:
                # Must also meet displacement threshold
                if float(row[1]['TRACK_DISPLACEMENT']) < displacement_threshold:
                    csv.drop(axis=0, inplace=True, labels=[row[0]])

    output_data: [float] = [0 for _ in range(len(csv.columns))]

    for i, item in enumerate(csv.columns):
        output_data[i] += sum([float(sub_item)
                              for sub_item in csv[item]])

    final_num_rows: int = len(csv)

    for i in range(len(output_data)):
        if final_num_rows == 0:
            print('Warning! No tracks remain!')
            output_data[i] = None
        else:
            output_data[i] /= final_num_rows

    if initial_num_rows != final_num_rows:
        print('Filtered out', initial_num_rows -
              final_num_rows, 'tracks, leaving', final_num_rows)

    return output_data


def graph_column(table: pd.DataFrame, column_name: str, file_name: str | None = None) -> bool:
    if column_name not in table.columns:
        return False

    if file_name is None:
        file_name = column_name

    plt.clf()

    plt.plot(table[column_name])

    plt.title('Unfiltered Track-Wise Mean ' +
              column_name + '\nby Applied Frequency')
    plt.xlabel('Applied Frequency')
    plt.ylabel(column_name)

    plt.savefig(file_name)

    return True


def graph_column_with_bars(table: pd.DataFrame, column_name: str,
                           bar_column_name: str, file_name: str | None = None) -> bool:
    if column_name not in table.columns or bar_column_name not in table.columns:
        return False

    if file_name is None:
        file_name = column_name

    plt.clf()

    plt.plot(table[column_name])

    minus_bar: [float] = [table[column_name][i] - table[bar_column_name][i]
                          for i in range(len(table[column_name]))]
    plus_bar: [float] = [table[column_name][i] + table[bar_column_name][i]
                         for i in range(len(table[column_name]))]

    plt.plot(minus_bar)
    plt.plot(plus_bar)

    plt.title('Unfiltered Track-Wise Mean ' + column_name +
              '\nby Applied Frequency (Plus or Minus ' + bar_column_name + ')')
    plt.xlabel('Applied Frequency')
    plt.ylabel(column_name)

    plt.savefig(file_name)

    return True


if __name__ == '__main__':
    print('Getting current folder...')

    folder = getcwd()

    print('Analyzing input data...')

    # Internal string representation of the frequencies
    names: [str] = [str(f) + 'khz' for f in frequencies]

    # Output array for data
    array = zeros(shape=(len(names), 7))

    # Analyze files

    brownian_speed_threshold: float = 0.0
    brownian_displacement_threshold: float = 0.0

    for i, name in enumerate(names):
        start: float = time()

        array[i] = do_file(folder + sep + name,
                           brownian_displacement_threshold,
                           brownian_speed_threshold)

        end: float = time()

        if i == 0:
            brownian_speed_threshold = array[0][1]
            brownian_displacement_threshold = array[0][0]

        print(name, 'took', round(end - start, 5), 'seconds.')

    print('Generating output .csv file...')

    out_csv: pd.DataFrame = pd.DataFrame(array,
                                         columns=col_names,
                                         index=names)
    out_csv.to_csv('track_data_summary.csv')

    print('Generating graphs...')

    graph_column_with_bars(out_csv, 'TRACK_MEAN_SPEED', 'TRACK_STD_SPEED')
    graph_column_with_bars(out_csv, 'TRACK_MEDIAN_SPEED', 'TRACK_STD_SPEED')

    for column_name in col_names:
        if (column_name != 'TRACK_MEAN_SPEED'
                and column_name != 'TRACK_MEDIAN_SPEED'
                and column_name != 'TRACK_STD_SPEED'):
            graph_column(out_csv, column_name)

    print('Done.')

    exit(0)
