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

from typing import *
import pandas as pd
from matplotlib import pyplot as plt
import os
import sys
import re

import name_fixer


class File:
    '''
    A lightweight class representing a single file. Contains the
    path used to obtain it (name), the data .csv file (data),
    and the standard deviation .csv file (stds). Used in later
    functions.
    '''

    def __init__(self, name: str, data: pd.DataFrame, stds: pd.DataFrame):
        self.name = name
        self.data = data
        self.stds = stds

    def __repr__(self) -> str:
        return self.name


# The set of all possible positions. A file should match only one.
z_position_filters: [str] = ['8940', '8960', '8965', '8980', '8985', '8990',
                             '9010', '9015', '9035', '9040', '9060', '9080', '9090',
                             '9115', '9140', '9180', '9197',
                             '9205', '9230', '9240', '9255', '9265', '9280', '9290',
                             '9305', '9315', '9340',
                             'top-100','top-97', 'top-75', 'top-50', 'top-25', 'top(?!-)',
                             'bot(?!\\+)', 'bot\\+25', 'bot\\+50', 'bot\\+75', 'bot\\+100']

# The voltage filters to use
voltages: Dict[str, str] = {'5[_ ]?[vV]' : '5v',
                            '8[_ ]?[vV]' : '8v',
                            '10[_ ]?[vV]' : '10v',
                            '12[_ ]?[vV]' : '12v',
                            '15[_ ]?[vV]' : '15v',
                            '16[_ ]?[vV]' : '16v',
                            '20[_ ]?[vV]' : '20v'}

# The frequency filters to use
frequencies: Dict[str, str] = {r'^0\.' : '0 Hz',
                               r'^1000\.' : '1 kHz',
                               r'^5000\.' : '5 kHz',
                               r'^10000\.' : '10 kHz',
                               r'^25000\.' : '25 kHz',
                               r'^50000\.' : '50 kHz',
                               r'^75000\.' : '75 kHz',
                               r'^100000\.' : '100 kHz'}


def velocity_vs_height(on: List[File], frequency: str) -> Tuple[List[str], List[float], List[float]]:
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
        for filter in z_position_filters:

            # If the current filter matches, append
            if re.findall(filter, file.name):

                name: str = filter
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

    # Load all .csv files in the cwd
    print('Fetching files from pattern ' + pattern + "...")
    files: List[File] = []
    found_names: [str] = name_fixer.find_all(pattern)

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
            temp = File(name, pd.read_csv(name), pd.read_csv(name.replace('.csv', '_stds.csv')))
            files.append(temp)
        
        except Exception as e:
            pass
    
    # Graph set A (see above)
    print('Graphing by voltage...')
    for voltage in voltages:
        plt.clf()
        plt.title('Mean Straight Line Speed at ' + voltages[voltage] + ', ' + pattern + ' by Applied Frequency')

        plt.xlabel('Height Label')
        plt.ylabel('Mean Straight Line Speed (Pixels / Frame)')
        plt.xticks(ticks=[i for i in range(len(z_position_filters))],
                   labels=z_position_filters,
                   rotation=45)

        # Build the set of all files matching frequency and voltage
        cur_files = [file for file in files if re.findall(voltage, file.name)]

        successes: int = 0
        for frequency in frequencies:

            # Extract data to graph
            heights, velocities, stds = velocity_vs_height(cur_files, frequency)

            if len(heights) == 0:
                continue
            else:
                successes += 1

            # Graph data
            plt.scatter(heights, velocities, label=frequencies[frequency])
            plt.errorbar(heights, velocities, yerr=stds)

        if successes == 0:
            print(f'Skipping voltage graph {voltages[voltage]}')
            continue

        # Save labels on graph
        lgd = plt.legend(bbox_to_anchor=(1.1, 1.05))

        # Save and close graph locally
        plt.savefig(clean_pattern + '_' + voltages[voltage] + '.png',
            bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.close()

    # Graph set B (see above)
    print('Graphing by frequency...')
    for frequency in frequencies:
        plt.clf()
        plt.title('Mean Straight Line Speed at ' + frequencies[frequency] + ', ' + pattern + ' by Voltage')

        plt.xlabel('Height Label')
        plt.ylabel('Mean Straight Line Speed (Pixels / Frame)')
        plt.xticks(ticks=[i for i in range(len(z_position_filters))],
                   labels=z_position_filters,
                   rotation=45)

        successes: int = 0
        for voltage in voltages:

            # Build the set of all files matching voltage
            cur_files = [file for file in files if re.findall(voltage, file.name)]
            
            # Extract data to graph
            heights, velocities, stds = velocity_vs_height(cur_files, frequency)

            if len(heights) == 0:
                continue
            else:
                successes += 1

            # Graph data
            plt.scatter(heights, velocities, label=voltages[voltage])
            plt.errorbar(heights, velocities, yerr=stds)

        if successes == 0:
            print(f'Skipping frequency graph {frequencies[frequency]}')
            continue

        # Save labels on graph
        lgd = plt.legend(bbox_to_anchor=(1.1, 1.05))

        # Save and close graph locally
        plt.savefig(clean_pattern + '_' + frequencies[frequency] + '.png',
            bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.close()

    # Exit
    print('Done.')
    return


if __name__ == '__main__':
    if len(sys.argv) == 1:
        # Put specialized stuff here

        graph_all_matching('120um')    

        # graph_all_matching('120_um_Top_Down')
        # graph_all_matching('120_um_Bottom_Up')

        # graph_all_matching('240_um_Top_Down')
        # graph_all_matching('240_um_Bottom_Up')

    else:
        print('Running from command line arguments...')
        for arg in sys.argv:
            graph_all_matching(arg)
    
    exit(0)
