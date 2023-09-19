#!/usr/bin/python3

import filterer
import name_fixer

from matplotlib import pyplot as plt
import numpy as np
import time
import pandas as pd
import os

'''
Jordan Dehmel, 2023
jdehmel@outlook.com

Analyzes by voltage using collected data

Gets secondary save path from filterer.py

Preconditions:
- ./do_graphs.sh has been run
- filterer.secondary_save_path is not None, and is not a unit string
- Data .csv's have been saved at the designated secondary save path

Postconditions:
- A voltage-wise analysis .csv has been saved in the secondary save path
- Any relevant graphs have also been saved there

We want to save the following for both 5 microns and 10 microns (separately).
1) Average straight-line speed across all frequencies by voltage as csv
2) Graph for above
3) Straight-line speed for a given frequency by voltage as csv
4) Graphs for above

We also want to do the following.
5) After everything, display a 3d plt graph of straight-line speed
   by frequency and voltage

This file does NO FILTERING. It only works with data which has already
been filtered and saved by filterer.py.
'''

# File patterns to look for
# Uses RegEx pattern matching via 're' py module
kcl_a_pattern: str = 'KCL[_ ]1[_ ]X[_ ]10-4[_ ]M'
kcl_b_pattern: str = 'KCL[_ ]5[_ ]X[_ ]10-5[_ ]M'

pattern_5_micron: str = '.*5[ _]?[Mm]icrons?.*'
pattern_10_micron: str = '.*10[ _]?[Mm]icrons?.*'

file_patterns: [str] = ['(?<!1)5[_ ]?V[_ ]?', '10[_ ]?V[_ ]?', '15[_ ]?V[_ ]?']
file_patterns_human_readable: [str] = ['5v', '10v', '15v']

# Optional because it halts execution
do_3d_graph: bool = True

# Optional because it slows things down
do_2d_graphs: bool = True


def do_voltage_files(patterns: [str], larger_pattern: str = '.*', larger_pattern_2: str = '.*',
                     folder: str = None, title: str = '', output_prefix: str = None,
                     patterns_human_readable: [str] = None) -> None:
    if folder is not None:
        os.chdir(folder)

    if output_prefix is None:
        output_prefix = str(round(time.time(), 3)).replace('.', '_')

    # Get .csv real names
    candidates: [str] = name_fixer.find_all(larger_pattern)
    other: [str] = name_fixer.find_all(larger_pattern_2)

    # Union
    candidates = [item for item in candidates if item in other]

    candidates = [
        c for c in candidates if '.csv' in c and '_stds.csv' not in c]

    real_names: [str] = name_fixer.fix_names(patterns, given_names=candidates)

    # Screen pattern failures
    num_failed_patterns: int = len(
        [item for item in real_names if item is None])

    if num_failed_patterns != 0:
        print('Warning!', num_failed_patterns, 'files were not found!')

    real_names = [item for item in real_names if item is not None]

    # Load .csv files
    files: [pd.DataFrame] = [None for _ in real_names]

    for i, name in enumerate(real_names):
        try:
            files[i] = pd.read_csv(name)
        except:
            print('Failed to open file', name)
            files[i] = None

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
                                        output_prefix + 'sls_by_voltage.png')

        # Build output graphs from B
        # Save output graphs from B

        pass

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

    return


if __name__ == '__main__':
    if filterer.secondary_save_path == '' or filterer.secondary_save_path is None:
        print('Fatal error: Could not find secondary save location.')

        exit(1)

    # KCL A stuff

    # 5 micron stuff
    do_voltage_files(patterns=file_patterns,
                     larger_pattern=pattern_5_micron,
                     larger_pattern_2=kcl_a_pattern,
                     folder=filterer.secondary_save_path,
                     title='5 Micron Colloid Straight Line Speed by Frequency and Voltage Applied (KCL 1 X 10-4 M)',
                     output_prefix='5_micron_kcl_a_',
                     patterns_human_readable=file_patterns_human_readable)

    # 10 micron stuff
    do_voltage_files(patterns=file_patterns,
                     larger_pattern=pattern_10_micron,
                     larger_pattern_2=kcl_a_pattern,
                     folder=filterer.secondary_save_path,
                     title='10 Micron Colloid Straight Line Speed by Frequency and Voltage Applied (KCL 1 X 10-4 M)',
                     output_prefix='10_micron_kcl_a_',
                     patterns_human_readable=file_patterns_human_readable)

    # KCL B stuff

    # 5 micron stuff
    do_voltage_files(patterns=file_patterns,
                     larger_pattern=pattern_5_micron,
                     larger_pattern_2=kcl_b_pattern,
                     folder=filterer.secondary_save_path,
                     title='5 Micron Colloid Straight Line Speed by Frequency and Voltage Applied (KCL 5 X 10-5 M)',
                     output_prefix='5_micron_kcl_b_',
                     patterns_human_readable=file_patterns_human_readable)

    # 10 micron stuff
    do_voltage_files(patterns=file_patterns,
                     larger_pattern=pattern_10_micron,
                     larger_pattern_2=kcl_b_pattern,
                     folder=filterer.secondary_save_path,
                     title='10 Micron Colloid Straight Line Speed by Frequency and Voltage Applied (KCL 5 X 10-5 M)',
                     output_prefix='10_micron_kcl_b_',
                     patterns_human_readable=file_patterns_human_readable)

    # Exit
    exit(0)
