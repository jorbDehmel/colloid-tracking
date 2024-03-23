'''
Takes in a folder to operate in. This folder should contain
files generated by speckle_to_track.py. It graphs them and saves
the graphs in the CWD.

Only filtered:
python3 speckle_graphing.py ~/data/2-21-2024-data/120um/8v/ \
    '.*' '.*\.(filtered|control)$'

Only non-filtered:
python3 speckle_graphing.py ~/data/2-21-2024-data/120um/8v/ \
    '.*' '.*_tracks\.csv$'
'''

import sys
import os
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import name_fixer
import speckle


files: Dict[str, str] = {
    r'control[0-9]*_tracks\.csv': '0khz',
    r'0\.5khz[0-9]*_tracks\.csv': '0.5khz',
    r'0\.8khz[0-9]*_tracks\.csv': '0.8khz',
    r'1khz[0-9]*_tracks\.csv': '1khz',
    r'2khz[0-9]*_tracks\.csv': '2khz',
    r'3khz[0-9]*_tracks\.csv': '3khz',
    r'(?<![\.2])5khz[0-9]*_tracks\.csv': '5khz',
    r'10khz[0-9]*_tracks\.csv': '10khz',
    r'25khz[0-9]*_tracks\.csv': '25khz',
    r'50khz[0-9]*_tracks\.csv': '50khz',
    r'75khz[0-9]*_tracks\.csv': '75khz',
    r'100khz[0-9]*_tracks\.csv': '100khz'}


graphing_duration_threshold: int = 0


def main(args: List[str]) -> int:
    '''
    The main function, to be called when this is run as a
    script.

    :param args: The command-line arguments.
    :returns: 0 on success, non-zero on failure.
    '''

    print('This script takes a root folder to iterate through,\n',
          'a folder pattern which sub-folders must match, and\n',
          'a file pattern which all `csv` files must match. It\n',
          'generates both scatter and line plots of the data\n',
          'within each subfolder as velocity by frequency.\n')

    if len(args) not in (3, 4):
        print('Please provide a root folder, a folder pattern,',
              'and optionally a file pattern as arguments.')
        return 1

    root_folder: str = args[1]
    folder_pattern: str = args[2]
    file_pattern: str = args[3] if len(args) == 4 else '.*'

    def do_root_folder(root: str) -> None:
        '''
        Graph the given folder and save locally. This folder
        should contain files matching the `files` patterns
        above.

        :param root: The folder to use
        '''

        print(f'Graphing folder {root}...')

        i: int = 0
        v_lines: List[int] = [0]
        speeds: List[float] = []

        means: List[float] = []
        stds: List[float] = []

        durations: List[int] = []

        old_dir: str = os.getcwd()
        os.chdir(root)

        # Look for all the frequency track files in this dir
        labels: List[str] = list(files)

        candidate_files: List[str] = name_fixer.find_all(file_pattern)

        fixed_files: List[str] = name_fixer.fix_names(labels, candidate_files)

        print('Files:')
        for file in fixed_files:
            print(f'\t{file}')

        zipped = [(item, files[labels[i]])
                  for i, item in enumerate(fixed_files) if item]

        fixed_files = [item[0] for item in zipped]
        labels = [item[1] for item in zipped]

        fixed_files = [file for file in fixed_files if file]

        for file in fixed_files:

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

        os.chdir(old_dir)

        plt.clf()
        plt.title(root + ' Speckle-Tracked')

        # Do individual point data
        plt.scatter(list(range(i)), speeds, c='b')
        plt.vlines(v_lines, ymin=0, ymax=max(speeds))

        # Do means and STDs
        plt.scatter(v_lines[:len(means)], means, c='r')

        plt.errorbar(v_lines[:len(means)], means, yerr=stds)

        plt.savefig(root.replace('/', '_') + '_speckle_scatter.png')

        plt.clf()

        # Simple plot
        plt.title(root + ' Speckle-Tracked')
        plt.plot(labels, means)
        plt.errorbar(labels, means, yerr=stds)

        plt.savefig(root.replace('/', '_') + '_speckle_plot.png')

        # Simple plot CSV version
        d: Dict[str, List[Any]] = {}

        d['CHAMBER_HEIGHT'] = labels
        d['SLS_MEAN'] = means
        d['SLS_STD'] = stds

        pd.DataFrame(d).to_csv(root.replace('/', '_') + '_speckle_plot.csv')

    speckle.for_each_dir(do_root_folder, root_folder, folder_pattern)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
