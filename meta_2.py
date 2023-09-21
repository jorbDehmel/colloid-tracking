#!/usr/bin/python3

import name_fixer
import pandas as df
import os
from matplotlib import pyplot as plt

import reverser

'''
An analysis wherein all data from a given voltage is
on the same graph.
'''

'''
Output table structure:

rows are frequency applied

columns are [voltage, solution, particle size, mean straight line speed, mean straight line speed std]
'''

# Relevant columns
columns: [str] = ['VOLTAGE', 'SOLUTION',
                  'SIZE_MICRONS', 'FREQUENCY_HZ', 'STRAIGHT_LINE_SPEED_PIXELS',
                  'STRAIGHT_LINE_SPEED_STD']

# Frequencies measured
frequencies: [str] = ['0.0', '800.0', '1000.0', '10000.0', '25000.0',
                      '50000.0', '75000.0', '100000.0', '150000.0', '200000.0', '300000.0']

# Where to save the .csv file
save_location: str = '/home/jorb/Programs/physicsScripts/output.csv'

# Directory to work in
dir: str = '/home/jorb/data_graphs/'


# Returns ([data], [std_data])
def load_voltage(pattern: str, save_path: str,
                 secondary_save_path: str, voltage: float,
                 do_graphs: bool = True,
                 transitions: [str] = ['10000.0', '10000.0', '10000.0']) -> ([df.DataFrame], [df.DataFrame], [str]):
    # Get candidates
    candidates: [str] = name_fixer.find_all(pattern)
    candidates = [c for c in candidates if 'stds' not in c]

    # Load files
    files: [df.DataFrame] = [None for _ in candidates]
    std_files: [df.DataFrame] = [None for _ in candidates]

    for i, name in enumerate(candidates):
        try:
            files[i] = df.read_csv(name)
        except:
            files[i] = None

        try:
            std_files[i] = df.read_csv(name[:-4] + '_stds.csv')
        except:
            std_files[i] = None

    if do_graphs:
        # Clean file names
        cleaned_names: [str] = []
        for item in candidates:
            name: str = ''

            if '5_Micron' in item:
                name += '5 micron '
            elif '10_Micron' in item:
                name += '10 micron '

            if 'KCL_1' in item:
                name += 'KCL 1 X 10-4 M'
            elif 'KCL_5' in item:
                name += 'KCL 5 X 10-5 M'

            cleaned_names.append(name)

        # Make graphs

        plt.rc('font', size=6)
        plt.figure(dpi=200)
        plt.clf()

        plt.ylabel('Mean Straight Line Speed (Pixels / Frame)')
        plt.xlabel('Applied Frequency (Hertz)')

        plt.title(str(voltage) +
                  'v Mean Straight Line Speed Relative to Cross Over')

        for i, file in enumerate(files):
            data: [float] = file['MEAN_STRAIGHT_LINE_SPEED'].astype(
                float).to_list()

            names: [str] = [str(n[1][0])
                            for n in file.iterrows()]

            cleaned_name: str = cleaned_names[i % len(names)]

            '''
            Must follow the following order:

            0 - 5 micron KCL 1
            1 - 10 micron KCL 1
            2 - 5 micron KCL 5
            3 - 10 micron KCL 5
            '''
            cur_transition: str = ''

            if cleaned_name == '5 micron ' + 'KCL 1 X 10-4 M':
                cur_transition = transitions[0]
            if cleaned_name == '10 micron ' + 'KCL 1 X 10-4 M':
                cur_transition = transitions[1]
            if cleaned_name == '5 micron ' + 'KCL 5 X 10-5 M':
                cur_transition = transitions[2]
            if cleaned_name == '10 micron ' + 'KCL 5 X 10-5 M':
                cur_transition = transitions[3]

            reverser.graph_relative(
                data, cur_transition, names, None, None, None, False, False, cleaned_name)

            # plt.plot(names, data, label=cleaned_names[i % len(names)])

        plt.legend()

        if save_path is not None:
            plt.savefig(save_path + '.png')

        if secondary_save_path is not None:
            plt.savefig(secondary_save_path + save_path + '.png')

    return (files, std_files, cleaned_names)


def unpack_single_voltage(data: ([df.DataFrame], [df.DataFrame], [str]),
                          array: [[float]], voltage: float) -> None:
    files, std_files, names = data

    for i, name in enumerate(names):
        row: [] = [None for _ in columns]

        row[0] = voltage

        if 'KCL 1 X 10-4 M' in name:
            row[1] = 'KCL 1 X 10-4 M'
        elif 'KCL 5 X 10-5 M' in name:
            row[1] = 'KCL 5 X 10-5 M'

        if '5 micron' in name:
            row[2] = 5.0
        elif '10 micron' in name:
            row[2] = 10.0

        # Iterate over frequencies herein
        data_rows = [item[1] for item in files[i].iterrows()]
        std_rows = [item[1] for item in std_files[i].iterrows()]

        for row_index in range(len(data_rows)):
            row_copy = [item for item in row]

            data_row = data_rows[row_index]
            std_row = std_rows[row_index]

            # Set frequency
            row_copy[3] = data_row[0]

            # Set mean sls
            row_copy[4] = data_row['MEAN_STRAIGHT_LINE_SPEED']

            # Set mean sls std
            row_copy[5] = std_row['MEAN_STRAIGHT_LINE_SPEED_STD']

            # print(row)
            array.append(row_copy)

    return


if __name__ == '__main__':
    os.chdir(dir)
    print('Working in directory', os.getcwd())

    # Voltage independent transition frequencies
    '''
    Must follow the following order:

    0 - 5 micron KCL 1
    1 - 10 micron KCL 1
    2 - 5 micron KCL 5
    3 - 10 micron KCL 5

    They must be in hertz.
    '''

    '''
    # Real values:
    voltage_independent_transitions: [str] = [
        14500,
        12500,
        10500,
        5500
    ]
    '''

    # Filler values:
    voltage_independent_transitions: [str] = ['10000.0' for _ in range(4)]

    data_5v: ([df.DataFrame], [df.DataFrame], [str]) = load_voltage('(?<!1)5[_ ]?[Vv].*\\.csv', '5v',
                                                                    '/home/jorb/Programs/physicsScripts/',
                                                                    5.0,
                                                                    transitions=voltage_independent_transitions)
    data_10v: ([df.DataFrame], [df.DataFrame], [str]) = load_voltage('10[_ ]?[Vv].*\\.csv', '10v',
                                                                     '/home/jorb/Programs/physicsScripts/',
                                                                     10.0,
                                                                     transitions=voltage_independent_transitions)
    data_15v: ([df.DataFrame], [df.DataFrame], [str]) = load_voltage('15[_ ]?[Vv].*\\.csv', '15v',
                                                                     '/home/jorb/Programs/physicsScripts/',
                                                                     15.0,
                                                                     transitions=voltage_independent_transitions)

    array: [[float]] = []

    # Do 5v stuff
    unpack_single_voltage(data_5v, array, 5.0)

    # Do 10v stuff
    unpack_single_voltage(data_10v, array, 10.0)

    # Do 15v stuff
    unpack_single_voltage(data_15v, array, 15.0)

    df_array: df.DataFrame = df.DataFrame(array,
                                          columns=columns)
    df_array.to_csv(save_location)

    exit(0)
