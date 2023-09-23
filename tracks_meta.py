#!/usr/bin/python3

import os
import sys
import pandas as df
from matplotlib import pyplot as plt

import reverser

# Meta analysis for 'tracks' data (sine, ramp, etc)

tracks_path: str = '/home/jorb/data/tracks'
voltages: [float] = [5.0, 10.0, 15.0, 20.0]
secondary_save_path: str = '/home/jorb/data/tracks/processed/'


def load_from_walk(where: str, look_for: str = '.csv', std_id: str = '_stds') -> [(str, df.DataFrame, df.DataFrame)]:
    std_file_paths: [str] = []
    file_paths: [str] = []

    # Collect all data paths from tracks_path via walk
    for (path, _, filenames) in os.walk(where, followlinks=True):
        for name in filenames:
            if look_for in name:
                if std_id in name:
                    if path + name not in std_file_paths:
                        std_file_paths.append(path + '/' + name)
                elif path + name not in file_paths:
                    file_paths.append(path + '/' + name)

    # Sort file paths into a predictable order
    file_paths.sort()
    std_file_paths.sort()

    # Open files and zip
    files: [(str, df.DataFrame, df.DataFrame)] = []
    for path in file_paths:
        try:
            file: df.DataFrame = df.read_csv(path)
        except:
            continue

        try:
            std_file: df.DataFrame = df.read_csv(path[:-4] + "_stds.csv")
        except:
            std_file = None

        files.append((path, file, std_file))

    # Return
    return files


if __name__ == '__main__':
    files: [(str, df.DataFrame, df.DataFrame)] = load_from_walk(
        tracks_path, 'track_data_summary.csv')

    print('Loaded', len(files), 'files.')

    # Turn to format which reverser.py takes
    ordered_data: [[float]] = []
    ordered_turning_points: [str] = []
    ordered_labels: [[str]] = []
    ordered_line_labels: [str] = []
    ordered_errors: [[float]] = []

    for item in files:
        ordered_line_labels.append(item[0])

        data: [float] = [row[1]['MEAN_STRAIGHT_LINE_SPEED']
                         for row in item[1].iterrows()]
        std_data: [float] = [row[1]['MEAN_STRAIGHT_LINE_SPEED_STD']
                             for row in item[2].iterrows()]

        ordered_data.append(data)
        ordered_errors.append(std_data)

        ordered_labels.append([row[1][0] for row in item[1].iterrows()])

    save_paths: [str] = [secondary_save_path + 'RELATIVE_SLS',
                         '/home/jorb/Programs/physicsScripts/data.png']
    axis_labels = ('Applied Frequency (Hz)',
                   'Relative Mean Straight Line Speed (Pixels / Frame)')
    subtitle: str = '(With Interpolated Crossover Point, Plus or Minus 1 STD)'

    ordered_turning_points = [10000.0 for _ in ordered_data]

    plt.rc('font', size=6)
    plt.figure(dpi=200)
    plt.clf()

    reverser.graph_multiple_relative(
        ordered_data,
        ordered_turning_points,
        ordered_labels,
        save_paths,
        axis_labels,
        ordered_line_labels,
        subtitle,
        ordered_errors
    )

    reverser.graph_multiple_relative_individually(
        ordered_data,
        None,
        ordered_labels,
        save_paths,
        axis_labels,
        ordered_line_labels,
        subtitle,
        ordered_errors
    )

    exit(0)
