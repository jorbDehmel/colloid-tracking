'''
Pet project because I think it'll look cool. Scatter plot, not
line plot.

x: Frequency
y: Chamber Height
z: Particle mobility
'''

import sys
from typing import List, Dict
from matplotlib import pyplot as plt
import pandas as pd

# Dict of height folders w/ labels. These go off some given root folder.
height_folders: Dict[str, str] = {
    'bot': 'bot/analysis',
    'bot+25': 'bot+25/analysis',
    'bot+50': 'bot+50/analysis',
    'bot+75': 'bot+75/analysis',
    'bot+100': 'bot+100/analysis'
}

# Dict of files to load. Each should be track file within a height folder.
within_height_files: Dict[str, str] = {
    'control': 'control_tracks.csv',
    '1khz': '1khz_tracks.csv',
    '5khz': '5khz_tracks.csv',
    '25khz': '25khz_tracks.csv',
    '50khz': '50khz_tracks.csv',
    '75khz': '75khz_tracks.csv',
    '100khz': '100khz_tracks.csv'
}


def load_file_speed_list(path: str) -> List[float]:
    '''
    Returns a list of all mobilities in a given file.
    '''

    frame: pd.DataFrame = pd.read_csv(path)
    frame.drop(inplace=True, labels=[0, 1, 2])

    data: List[float] = [float(row[1]['MEAN_STRAIGHT_LINE_SPEED'])
                         for row in frame.iterrows()]

    return data


if __name__ == '__main__':
    fig = plt.figure()
    ax1 = fig.add_subplot(projection='3d')

    root_folder: str = '~/data/120um_16v_speckles_clean'

    for i, height_folder in enumerate(height_folders):

        bins: Dict[str, List[float]] = {}

        for file, name in within_height_files.items():
            full_path: str = (root_folder
                              + '/'
                              + height_folders[height_folder]
                              + '/'
                              + name)
            bins[file] = load_file_speed_list(full_path)

        # Graph collected speeds by bin

        xs: List[float] = []
        zs: List[float] = []

        for k, label in enumerate(bins):
            speeds = bins[label]

            xs += [k + (j / len(speeds)) for j in range(len(speeds))]
            zs += speeds

        ax1.scatter(xs, [i for _ in xs], zs, label=height_folder)

    ax1.set_xlabel('Frequency')
    ax1.set_ylabel('Chamber Depth')
    ax1.set_zlabel('Speed')

    plt.suptitle('Speed (Pixels / Frame) By Frequency and Chamber Depth')
    plt.title(root_folder)

    plt.legend()
    plt.show()

    sys.exit(0)
