'''
Takes in a folder to operate in. This folder should contain
files generated by speckle_to_track.py. It graphs them and saves
the graphs in the CWD.
'''

import sys
from typing import List
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt


files: List[str] = [
    'control_tracks.csv',
    '1khz_tracks.csv',
    '5khz_tracks.csv',
    '10khz_tracks.csv',
    '25khz_tracks.csv',
    '50khz_tracks.csv',
    '75khz_tracks.csv',
    '100khz_tracks.csv']
labels: List[str] = [
    'control',
    '1khz',
    '5khz',
    '10khz',
    '25khz',
    '50khz',
    '75khz',
    '100khz']


graphing_duration_threshold: int = 0


if __name__ == '__main__':
    assert len(sys.argv) == 2

    root: str = sys.argv[1]
    i: int = 0
    v_lines: List[int] = [0]
    speeds: List[float] = []

    means: List[float] = []
    stds: List[float] = []

    durations: List[int] = []

    for file in files:

        df: pd.DataFrame = pd.read_csv(root + '/' + file)
        df.drop(inplace=True, labels=[0, 1, 2])

        cur_speeds: List[float] = []
        for row in df.iterrows():
            durations.append(int(row[1]['TRACK_DURATION']))

            if int(row[1]['TRACK_DURATION']) < graphing_duration_threshold:
                print('Dropping')
                continue

            i += 1
            cur_speeds.append(float(row[1]['MEAN_STRAIGHT_LINE_SPEED']))

        speeds += cur_speeds
        means.append(np.mean(cur_speeds))
        stds.append(np.std(cur_speeds))

        v_lines.append(i)

    plt.title(root + ' Speckle-Tracked')

    # Do individual point data
    plt.scatter([j for j in range(i)], speeds, label='Speckles', c='b')
    plt.vlines(v_lines, ymin=0, ymax=max(speeds))

    # Do means and STDs
    plt.scatter(v_lines[:len(means)], means, c='r')

    plt.errorbar(v_lines[:len(means)], means, yerr=stds)

    print(
        f'Mean duration: {np.mean(durations)} Duration STD: {np.std(durations)}')

    plt.savefig(root.replace('/', '_') + '_speckle_scatter.png')

    plt.clf()

    plt.title(root + ' Speckle-Tracked')
    plt.plot(labels, means)
    plt.errorbar(labels, means, yerr=stds)

    plt.savefig(root.replace('/', '_') + '_speckle_plot.png')
