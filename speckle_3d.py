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
import os
import name_fixer


# Dict of height folders w/ labels. These go off some given root folder.
height_folders: Dict[str, str] = {
    'bot': 'bot/',
    'bot+25': 'bot+25/',
    'bot+50': 'bot+50/',
    'bot+75': 'bot+75/',
    'bot+100': 'bot+100/'
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


def main(args: List[str]) -> int:
    '''
    The main file for when this is being run as a script.

    :param args: The command-line arguments.
    :returns: 0 on success, non-zero on failure.
    '''

    fig = plt.figure()
    ax1 = fig.add_subplot(projection='3d')

    if len(args) == 1:
        print('Please provide a root folder as a command-line arg.')
        sys.exit(1)

    original_cwd: str = os.getcwd()
    root_folder: str = args[1]

    os.chdir(root_folder)

    for i, pattern in enumerate(height_folders):

        results: List[str] = name_fixer.find_all_recursive(pattern)
        assert len(results) >= 1

        height_folder: str = results[0]

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

    os.chdir(original_cwd)

    ax1.set_xlabel('Frequency')
    ax1.set_ylabel('Chamber Depth')
    ax1.set_zlabel('Speed')

    plt.suptitle('Speed (Pixels / Frame) By Frequency and Chamber Depth')
    plt.title(root_folder)

    plt.legend()
    plt.show()

    sys.exit(0)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
