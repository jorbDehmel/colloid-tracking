'''
Makes some comparisons by voltage and frequency for height-wise
data.

All graphs produced herein should be velocity vs. height.

Does this process for each pattern, searching for files ONLY
in the current working directory.

Graph set A:
- each graph is a single voltage
- each curve is a frequency

Graph set B:
- each graph is a single frequency
- each curve is a voltage

Jordan Dehmel, 2023
jdehmel@outlook.com
jedehmel@mavs.coloradomesa.edu
'''

import os
import sys
import re
from typing import List, Dict, Tuple, Union
import pandas as pd
from matplotlib import pyplot as plt

import name_fixer


class File:
    '''
    A lightweight class representing a single file. Contains the
    path used to obtain it (name), the data .csv file (data),
    and the standard deviation .csv file (std's). Used in later
    functions.
    '''

    def __init__(self, name: str, data: pd.DataFrame, stds: pd.DataFrame):
        self.name = name
        self.data = data
        self.stds = stds

    def __repr__(self) -> str:
        return self.name


# The set of all possible positions. A file should match only one.
# Honestly, I have no idea what these mean or how to compare the
# multiple different formats.
z_position_filters: [str] = ['8940', '8960', '8965', '8980', '8985', '8990',
                             '9010', '9015', '9035', '9040', '9060', '9080', '9090',
                             '9115', '9140', '9180', '9197',
                             '9205', '9230', '9240', '9255', '9265', '9280', '9290',
                             '9305', '9315', '9340',
                             'top-100', 'top-97', 'top-75', 'top-50', 'top-25', 'top(?!-)',
                             'bot(?!\\+)', 'bot\\+25', 'bot\\+50', 'bot\\+70', 'bot\\+75',
                             'bot\\+100', 'bot\\+190', 'bot\\+210']

# The voltage filters to use
voltages: Dict[str, str] = {'(?<!1)5[_ ]?[vV]': '5v',
                            '8[_ ]?[vV]': '8v',
                            '10[_ ]?[vV]': '10v',
                            '12[_ ]?[vV]': '12v',
                            '15[_ ]?[vV]': '15v',
                            '16[_ ]?[vV]': '16v',
                            '20[_ ]?[vV]': '20v'}
skip_voltage: bool = False

# The frequency filters to use
frequencies: Dict[str, str] = {r'^0\.': '0 Hz',
                               r'^1000\.': '1 kHz',
                               r'^5000\.': '5 kHz',
                               r'^10000\.': '10 kHz',
                               r'^25000\.': '25 kHz',
                               r'^50000\.': '50 kHz',
                               r'^75000\.': '75 kHz',
                               r'^100000\.': '100 kHz'}


def velocity_vs_height(
        on: List[File],
        frequency: str) -> Tuple[List[str], List[float], List[float]]:
    '''
    :param on:  The list of files to operate on
    :param frequency:   The frequency pattern to use for the output
    :return:    A 3-tuple of the heights, followed by the velocities,
                followed by standard deviations..

    Gets the data required to graph a given dataset's velocity
    by its height.
    '''

    items: List[Tuple[List[str], List[float], List[float]]] = []

    # Iterate over files
    for file in on:

        # For each file, append the first height filter that
        # matches it to heights
        for filter_name in z_position_filters:

            # If the current filter matches, append
            if re.findall(filter_name, file.name):

                name: str = filter_name
                data: Union[None, float] = None
                std: Union[None, float] = None

                # Extract velocity and append
                for row in file.data.iterrows():
                    if re.findall(frequency, str(row[1][0])):
                        data = float(row[1]['MEAN_STRAIGHT_LINE_SPEED'])
                        break

                for row in file.stds.iterrows():
                    if re.findall(frequency, str(row[1][0])):
                        std = float(row[1]['MEAN_STRAIGHT_LINE_SPEED_STD'])
                        break

                if data is None or std is None:
                    continue

                items.append((name, data, std))

    # Sort items
    items.sort(key=lambda i: z_position_filters.index(i[0]))

    # Deconstruct sorted items in the correct order
    heights: [str] = [item[0] for item in items]
    velocities: [float] = [item[1] for item in items]
    stds: [float] = [item[2] for item in items]

    return (heights, velocities, stds)


def graph_all_matching(pattern: str = r'.*\.csv$') -> None:
    '''
    :param pattern: The RegEx to graph matching files of.
    :return: Nothing

    Graph all files matching a certain RegEx pattern.
    '''

    # Load all .csv files in the cwd
    print('Fetching files from pattern ' + pattern + "...")
    files: List[File] = []
    found_names: [str] = name_fixer.find_all(pattern)

    found_names = [item for item in found_names if item[-4:] != '.png']

    print('Found files:')
    for item in found_names:
        print('\t', item)

    clean_pattern: str = pattern.replace('.', '_')
    clean_pattern = clean_pattern.replace('/', '_')
    clean_pattern = clean_pattern.replace('\\', '_')
    clean_pattern = clean_pattern.replace('^', '_')
    clean_pattern = clean_pattern.replace('$', '_')

    # Make local names fully qualified (needed for pd.read_csv)
    cwd: str = os.getcwd()
    found_names = [cwd + '/' + name for name in found_names]

    # Iterate over names, construct into files
    for name in found_names:

        # If standard deviations, pass over
        if '_stds' in name:
            continue

        try:
            temp = File(name, pd.read_csv(name), pd.read_csv(
                name.replace('.csv', '_stds.csv')))
            files.append(temp)

        except Exception:
            pass

    # Graph set A (see above)
    print('Graphing by voltage...')
    for voltage, v_label in voltages.items():
        if skip_voltage:
            v_label = '16v'

        plt.clf()
        plt.title('Mean Straight Line Speed at ' +
                  v_label + ', ' + pattern + ' by Applied Frequency')

        plt.xlabel('Height Label')
        plt.ylabel('Mean Straight Line Speed (Pixels / Frame)')

        # Build the set of all files matching frequency and voltage
        if not skip_voltage:
            cur_files = [file for file in files if re.findall(
                voltage, file.name)]
        else:
            cur_files = files[:]

        successes: int = 0
        for frequency, f_label in frequencies.items():

            # Extract data to graph
            heights, velocities, stds = velocity_vs_height(
                cur_files, frequency)

            if len(heights) == 0:
                continue
            else:
                successes += 1

            # Graph data
            plt.scatter(heights, velocities, label=frequencies[frequency])
            plt.errorbar(heights, velocities, yerr=stds)

        if successes == 0:
            print(f'Skipping voltage graph {v_label}')
            continue

        # Save labels on graph
        lgd = plt.legend(bbox_to_anchor=(1.1, 1.05))

        # Save and close graph locally
        plt.savefig(clean_pattern + '_' + v_label + '.png',
                    bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.close()

        if skip_voltage:
            break

    # Graph set B (see above)
    print('Graphing by frequency...')
    for frequency, f_label in frequencies.items():
        plt.clf()
        plt.title('Mean Straight Line Speed at ' +
                  f_label + ', ' + pattern + ' by Voltage')

        plt.xlabel('Height Label')
        plt.ylabel('Mean Straight Line Speed (Pixels / Frame)')

        successes: int = 0
        for voltage, v_label in voltages.items():
            if skip_voltage:
                v_label = '16v'

            # Build the set of all files matching voltage
            if not skip_voltage:
                cur_files = [file for file in files if re.findall(
                    voltage, file.name)]

            # Extract data to graph
            heights, velocities, stds = velocity_vs_height(
                cur_files, frequency)

            if len(heights) == 0:
                continue

            successes += 1

            # Graph data
            plt.scatter(heights, velocities, label=v_label)
            plt.errorbar(heights, velocities, yerr=stds)

            if skip_voltage:
                break

        if successes == 0:
            print(f'Skipping frequency graph {f_label}')
            continue

        # Save labels on graph
        lgd = plt.legend(bbox_to_anchor=(1.1, 1.05))

        # Save and close graph locally
        plt.savefig(clean_pattern + '_' + f_label + '.png',
                    bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.close()

    # Exit
    print('Done.')
    return


if __name__ == '__main__':
    if len(sys.argv) == 1:
        # Put specialized stuff here

        graph_all_matching('120um')

    else:
        print('Running from command line arguments...')
        for arg in sys.argv:
            if arg[-3:] == '.py':
                continue

            graph_all_matching(arg)

    exit(0)
