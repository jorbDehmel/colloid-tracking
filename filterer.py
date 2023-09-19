#!/usr/bin/python3

'''
Jordan Dehmel, 2023
jdehmel@outlook.com
'''

import pandas as pd
from numpy import zeros, mean, std, percentile
import matplotlib.pyplot as plt
from os import *
from sys import *
from time import time
import name_fixer

# What columns to keep from the .csv files
col_names: [str] = ['TRACK_DISPLACEMENT', 'TRACK_MEAN_SPEED',
                    'TRACK_MEDIAN_SPEED', 'TRACK_MEAN_QUALITY',
                    'TOTAL_DISTANCE_TRAVELED', 'MEAN_STRAIGHT_LINE_SPEED',
                    'LINEARITY_OF_FORWARD_PROGRESSION']

# Columns which didn't originally exist, but will exist in our output .csv
extra_columns: [str] = ['INITIAL_TRACK_COUNT',
                        'FILTERED_TRACK_COUNT',
                        'STRAIGHT_LINE_SPEED_UM_PER_S']

# Flags for which -2 * STD filters to apply
# do_std_filter_flags: [bool] = [False, False, False, True, False, True, True]
# do_std_filter_flags: [bool] = [True, True, True, True, True, True, True]
do_std_filter_flags: [bool] = None

# Flags for which -1.5 * IQR filters to apply
do_iqr_filter_flags: [bool] = [False, False, False, True, False, True, False]
# do_iqr_filter_flags: [bool] = [True, False, True, True, True, True, True]

do_quality_percentile_filter: bool = True
quality_percentile_filter: float = 40.0

patterns: [str] = ['(^0 ?khz|control)', '(0.8 ?khz|800 ?hz)',
                   '^1 ?khz', '^10 ?khz', '^25 ?khz', '^50 ?khz',
                   '^75 ?khz', '^100 ?khz', '^150 ?khz', '^200 ?khz',
                   '^300 ?khz']

# The folder to operate on. Will be replaced by the cwd if ''
folder: str = ''

# Conversion from pixels/frame to um/s
conversion: float = 4 * 0.32

# Tends to erase everything
do_speed_thresh: bool = False

# Tends to work well
do_displacement_thresh: bool = True

# Tends to not do much
do_linearity_thresh: bool = False

# If not None, also save graphs here (w/ mangled prefix)
secondary_save_path: str = '/home/jorb/data_graphs/'

# If true, will only print warnings and errors
silent: bool = True

# Analyze a file with a given name, and return the results
# If speed_threshold is nonzero, any track with less speed will
# be filtered out. This is similar for the linearity and displacement
# thresholds. The std_drop_flags and iqr_drop_flags lists are
# arrays of booleans. If the ith item is True, that column
# will be filtered such that only items which remain are those
# which are above 2 STD/IQR below the mean for their column.
# Returns a duple containing the output data followed by
# the standard deviations.


def do_file(name: str, displacement_threshold: float = 0.0,
            speed_threshold: float = 0.0, linearity_threshold: float = 0.0,
            std_drop_flags: [bool] = None, iqr_drop_flags: [bool] = None) -> ([float], [float]):
    try:
        # Load file
        csv = pd.read_csv(name)
    except:
        print('Failed to open', name)
        return ([None for _ in col_names] + [None, None], [None for _ in col_names])

    # Drop useless data (columns)
    names_to_drop: [str] = []
    for column_name in csv.columns:
        if column_name not in col_names:
            names_to_drop.append(column_name)

    csv.drop(axis=1, inplace=True, labels=names_to_drop)

    # Ensure the columns are in the correct order (VITAL)
    assert csv.columns.to_list() == col_names

    # Drop useless data (rows)
    csv.drop(axis=0, inplace=True, labels=[0, 1, 2])

    # Used later
    initial_num_rows: int = len(csv)

    # Do thresholding here
    if do_speed_thresh or do_displacement_thresh or do_linearity_thresh or do_quality_percentile_filter:
        for row in csv.iterrows():
            if do_speed_thresh:
                # Must meet mean straight line speed threshold
                if float(row[1]['MEAN_STRAIGHT_LINE_SPEED']) < speed_threshold:
                    csv.drop(axis=0, inplace=True, labels=[row[0]])
                    continue

            if do_displacement_thresh:
                # Must also meet displacement threshold
                if float(row[1]['TRACK_DISPLACEMENT']) < displacement_threshold:
                    csv.drop(axis=0, inplace=True, labels=[row[0]])
                    continue

            if do_linearity_thresh:
                # Must pass linearity threshold
                if float(row[1]['LINEARITY_OF_FORWARD_PROGRESSION']) < linearity_threshold:
                    csv.drop(axis=0, inplace=True, labels=[row[0]])
                    continue

            if do_quality_percentile_filter:
                # Must pass quality threshold
                quality_percentile_threshold: float = percentile(
                    csv['TRACK_MEAN_QUALITY'].astype(float), q=[quality_percentile_filter])[0]

                if float(row[1]['TRACK_MEAN_QUALITY']) < quality_percentile_threshold:
                    csv.drop(axis=0, inplace=True, labels=[row[0]])
                    continue

    if csv.shape[0] == 0:
        print('Error! No items exceeded brownian thresholding.')

    # Do STD filtering if needed
    if std_drop_flags is not None and len(std_drop_flags) == len(csv.columns):

        # Collect STD's for the requested items
        std_values: [float] = [
            std(csv[col_name].astype(float)) if std_drop_flags[i] else 0.0 for i, col_name in enumerate(csv.columns)]

        # Collect means
        mean_values: [float] = [
            mean(csv[col_name].astype(float)) if std_drop_flags[i] else 0.0 for i, col_name in enumerate(csv.columns)]

        # Iterate over rows, dropping if needed
        for row in csv.iterrows():
            raw_list: [float] = row[1].astype(float).to_list()

            for i in range(len(raw_list)):
                if raw_list[i] < mean_values[i] - (2 * std_values[i]):
                    csv.drop(axis=0, inplace=True, labels=[row[0]])
                    break

    if csv.shape[0] == 0:
        print('Error! No items survived brownian thresholding and standard deviation filtering.')

    # Do IQR filtering if needed
    if iqr_drop_flags is not None and len(iqr_drop_flags) == len(csv.columns):

        # Calculate IQR values
        iqr_values: [float] = [0.0 for i in csv.columns]
        for i, col_name in enumerate(csv.columns):
            if iqr_drop_flags[i]:
                q1, q3 = percentile(csv[col_name].astype(float), [25, 75])
                iqr_values[i] = q3 - q1

        # Collect means
        mean_values: [float] = [
            mean(csv[col_name].astype(float)) if iqr_drop_flags[i] else 0.0 for col_name in csv.columns]

        # Iterate over rows, dropping if needed
        for row in csv.iterrows():
            raw_list: [float] = row[1].astype(float).to_list()

            for i in range(len(raw_list)):
                if raw_list[i] < mean_values[i] - (1.5 * iqr_values[i]):
                    csv.drop(axis=0, inplace=True, labels=[row[0]])
                    break

    if csv.shape[0] == 0:
        print('Error! No items survived brownian thresholding, STD filtering, and IQR filtering.')

    # Compile output data from filtered inputs
    final_num_rows: int = len(csv)

    output_data: [float] = [0.0 for _ in range(
        len(col_names) + len(extra_columns))]
    output_std: [float] = [0.0 for _ in range(len(col_names))]

    # Calculate means and adjusted STD's
    for i, item in enumerate(csv.columns):
        output_data[i] = mean(csv[item].astype(float).to_list())
        output_std[i] = std(csv[item].astype(float).to_list())

    for i in range(len(output_data)):
        if final_num_rows == 0:
            print('Warning! No tracks remain!')
            output_data[i] = None

    output_data[len(col_names)] = initial_num_rows
    output_data[len(col_names) + 1] = final_num_rows

    if output_data[5] is None:
        output_data[len(col_names) + 2] = None
    else:
        output_data[len(col_names) + 2] = output_data[5] * conversion

    # Output percent remaining
    if initial_num_rows != final_num_rows:
        print((name + ':')[-20:],
              'Filtered out', initial_num_rows -
              final_num_rows, 'tracks, leaving',
              final_num_rows, '(' +
              str(round(100 * final_num_rows / initial_num_rows, 3))
              + '% remain)')

    return (output_data, output_std)


def graph_column_with_bars(table: pd.DataFrame, bar_table: pd.DataFrame, column_name: str,
                           bar_column_name: str, file_name: (str | None) = None,
                           has_control: bool = False) -> bool:

    if column_name not in table.columns or bar_column_name not in bar_table.columns:
        return False

    if file_name is None:
        file_name = column_name

    plt.clf()

    plt.rc('font', size=6)

    minus_bar: [float] = [table[column_name][i] - bar_table[bar_column_name][i]
                          for i in range(len(table[column_name]))]

    plus_bar: [float] = [table[column_name][i] + bar_table[bar_column_name][i]
                         for i in range(len(table[column_name]))]

    if has_control:
        brownian_bar: [float] = [table[column_name][0]
                                 for _ in table[column_name]]
        plt.plot(brownian_bar)

    plt.plot(minus_bar)
    plt.plot(plus_bar)

    plt.plot(table[column_name])

    filter_status: str = ''

    # Create filter text
    if do_speed_thresh:
        filter_status += 'Speed-filtered '
    if do_displacement_thresh:
        filter_status += 'Displacement-filtered '
    if do_linearity_thresh:
        filter_status += 'Linearity-filtered '
    if do_quality_percentile_filter:
        filter_status += 'Quality-filtered '
    if do_quality_percentile_filter:
        filter_status += str(quality_percentile_filter) + \
            '-percentile-plus '
    if do_std_filter_flags is not None:
        filter_status += '2_STD_MIN-filtered '
    if do_iqr_filter_flags is not None:
        filter_status += '1.5_IQR_MIN-filtered '

    if filter_status == '':
        filter_status = 'Unfiltered '

    plt.title(name_fixer.get_cwd() + '\n' + filter_status + '\nMean ' + column_name +
              'by Applied Frequency (Plus or Minus ' + bar_column_name + ')')

    plt.xlabel('Applied Frequency (Hertz)')
    plt.ylabel(column_name)

    plt.savefig(file_name)

    if secondary_save_path is not None:
        plt.savefig(secondary_save_path +
                    name_fixer.get_cwd() + '_' + file_name)

    return True


if __name__ == '__main__':
    if folder == '' or folder is None:
        if len(argv) != 1:
            if not silent:
                print('Changing folder from arguments...')

            chdir(argv[1])

        if not silent:
            print('Getting current folder...')

        folder = getcwd()

    if not silent:
        print('Analyzing input data at', folder)

    # Internal string representation of the frequencies
    names: [str] = name_fixer.fix_names(patterns)
    has_control: bool = (names[0] is not None)

    # Drop any files which do not exist
    names = [name for name in names if name is not None]

    # Exit if no names remain
    if len(names) == 0:
        raise Exception('No files could be found.')

    # Output array for data
    array = zeros(shape=(len(names), len(col_names) + len(extra_columns)))
    std_array = zeros(shape=(len(names), len(col_names)))

    # Analyze files

    brownian_speed_threshold: float = 0.0
    brownian_displacement_threshold: float = 0.0
    brownian_linearity_threshold: float = 0.0

    for i, name in enumerate(names):
        if i == 0 and has_control:
            start: float = time()

            try:
                array[i], std_array[i] = do_file(folder + sep + name,
                                                 0.0, 0.0, 0.0,
                                                 None, None)
            except:
                print("ERROR DURING COLLECTION OF FILE", folder + sep + name)
                array[i] = [None for i in len(array[i])]
                std_array[i] = [None for i in len(std_array[i])]

            end: float = time()

            brownian_displacement_threshold = array[0][0]
            quality_threshold = array[0][3]
            brownian_speed_threshold = array[0][4]
            brownian_linearity_threshold = array[0][5]

        else:
            start: float = time()

            array[i], std_array[i] = do_file(folder + sep + name,
                                             brownian_displacement_threshold,
                                             brownian_speed_threshold,
                                             brownian_linearity_threshold,
                                             do_std_filter_flags,
                                             do_iqr_filter_flags)

            end: float = time()

        if not silent:
            print(name, 'took', round(end - start, 5), 'seconds.')

    if not silent:
        print('Generating output .csv file...')

    trimmed_names: [str] = [item[:8] for item in names]
    floated_names: [str] = [str(name_fixer.path_to_hz(item)) for item in names]

    out_csv: pd.DataFrame = pd.DataFrame(array,
                                         columns=(
                                             col_names + extra_columns),
                                         index=floated_names)
    out_csv.to_csv('track_data_summary.csv')

    std_csv: pd.DataFrame = pd.DataFrame(std_array,
                                         columns=(
                                             [name + '_STD' for name in col_names]),
                                         index=floated_names)
    std_csv.to_csv('track_data_summary_stds.csv')

    if secondary_save_path is not None:
        out_csv.to_csv(secondary_save_path +
                       name_fixer.get_cwd() + 'track_data_summary.csv')
        std_csv.to_csv(secondary_save_path +
                       name_fixer.get_cwd() + 'track_data_summary_stds.csv')

    if not silent:
        print('Generating graphs...')

    for column_name in col_names:
        graph_column_with_bars(
            out_csv, std_csv, column_name, column_name + '_STD',
            has_control=has_control)

    plt.clf()
    plt.rc('font', size=6)

    plt.title(name_fixer.get_cwd() +
              '\nInitial (Top) Vs. Final (Bottom) Track Counts')

    plt.plot(out_csv['INITIAL_TRACK_COUNT'])
    plt.plot(out_csv['FILTERED_TRACK_COUNT'])

    plt.savefig('TRACK_COUNT.png')

    if secondary_save_path is not None:
        plt.savefig(secondary_save_path +
                    name_fixer.get_cwd() + '_TRACK_COUNT')

    if not silent:
        print('Done.')

    exit(0)
