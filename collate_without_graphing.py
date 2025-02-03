'''
Collates means and standard deviations without trying to graph
or sort by frequency. This should be used for abnormal data.
'''

import sys
import re
from typing import List, Dict
import pandas as pd
import speckle


def main(args: List[str]) -> int:
    '''
    Main function. Operates on all TRACKS files.
    :param args: The CLI args
    :returns: Error code (0 on success)
    '''

    # Print info
    print(
        f'{__file__}: Collate arbitrary TRACKS w/o graphs.\n'
        'Takes in (root folder, target csv, regex pattern)\n'
        'and saves all matching files\' means and stds in the\n'
        'target file. This is a slight simplification of the\n'
        '`comparisons` script.')

    # Parse args
    if len(args) != 4:
        print(
            '3 args are required: Root folder, target file, '
            'and RE pattern.')
        return 2

    root: str = args[1]
    target: str = args[2]
    pattern: str = args[3]

    # Where we will save data
    means: Dict[str, float] = {}
    stds: Dict[str, float] = {}

    def do_single_frequency_file(file: str) -> None:
        '''
        Loads a single frequency's tracks file and loads the
        mean and std for straight line speed. Appends this
        information to external variables.

        :param file: The file to operate on.
        '''

        nonlocal means, stds, pattern

        if file in means or file in stds:
            print(f'Skipping repeated file `{file}`')
            return

        # Skip non-matching
        if not re.findall(pattern, file):
            print(f'Rejected non-matching file {file}')
            return
        elif 'ANOMALY' in file:
            print(f'Rejected anomalous file {file}')
            return
        elif not file.endswith('.csv'):
            print(f'Rejected non-csv file {file}')
            return
        elif 'tracks' not in file:
            print(f'Rejected non-tracks file {file}')
            return
        elif '/graphs/' in file:
            print(f'Rejected graph file {file}')
            return

        print(f'Accepted file {file}')

        # Load tracks file
        tracks: pd.DataFrame = pd.read_csv(file)
        tracks.drop([0, 1, 2], inplace=True)

        speeds = \
            tracks['MEAN_STRAIGHT_LINE_SPEED'].astype(float)

        # Calculate mean MEAN_STRAIGHT_LINE_SPEED
        mean: float = speeds.mean()

        # Calculate std MEAN_STRAIGHT_LINE_SPEED
        std: float = speeds.std()

        # Append to `means` and `stds`
        means[file] = mean
        stds[file] = std

    # Fetch all the data from the current frequency pattern
    speckle.for_each_file(
        do_single_frequency_file, root, pattern)

    if len(means) == 0:
        print('Failed to find any track data!')
        return 1

    # Save the data
    print(f'Saving collated data at {target}...')

    with open(target, mode='w', encoding='utf8') as f:
        f.write('file,mean_SLS,SLS_std,\n')
        for key, mean in means.items():
            f.write(f'{key.removeprefix(root)},{mean},{stds[key]},\n')

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
