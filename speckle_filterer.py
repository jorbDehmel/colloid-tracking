'''
Revamped filterer for speckle files, using the `speckle`
package.

Jordan Dehmel, 2024
jedehmel@mavs.coloradomesa.edu
jdehmel@outlook.com
'''

import sys
import os
import re
from typing import List
import speckle as s
from speckle import filters as f


# The RegEx pattern used to detect control files
control_pattern: str = r'(((?<![0-9])0 ?khz|control).*track|t(0 ?khz|control)).*\.csv'

# The Brownian threshold filter removes any track whose SLS is
# < BROWNIAN_MEAN_SLS + k * BROWNIAN_STD_SLS
k: float = 0


def main(args: List[str]) -> int:
    '''
    The main function to be called when this is being run as a
    script. This operates on each folder in the specified root
    directory, applying some number of filters to each.

    :param args: The command-line arguments.
    :returns: Zero on success, nonzero on failure.
    '''

    print('This program will recursively walk through a given',
          'folder and apply a Brownian SLS threshold to every',
          'item therein.')

    if len(args) != 2:
        print('Please provide 1 command-line argument: The root folder.')
        return 1

    root: str = args[1]
    total_dropped: int = 0
    total_remaining: int = 0

    files_skipped: List[str] = []
    files_done: List[str] = []

    folders_done: List[str] = []

    def filter_folder(dir_path: str) -> None:
        '''
        Apply filters to all files herein, then save them under
        a modified name.
        '''

        dir_path = os.path.realpath(dir_path)

        if dir_path in folders_done:
            return

        folders_done.append(dir_path)

        print(f'Filtering directory {dir_path}...')

        # Recurse on any subfolders which exist
        s.for_each_dir(filter_folder, dir_path, '[^.].*')

        # Find control
        fq_control_path: str = ''

        def find(path: str) -> None:
            nonlocal fq_control_path
            fq_control_path = path

        s.for_each_file(find, dir_path, r'.*' + control_pattern)

        if not fq_control_path:
            print('Failed to find control file.')
            return

        # Load control
        control: s.FreqFile = s.load_frequency_file(fq_control_path)

        # Extract brownian threshold
        threshold: float = control.sls_mean() + k * control.sls_std()

        def filter_single_file(file_path: str) -> None:
            '''
            Apply filters to this path, which is a single
            frequency file.
            '''

            nonlocal total_dropped, total_remaining, files_skipped

            file_path = os.path.realpath(file_path)

            print(f'Operating on file "{file_path}"')

            # Do not operate on control files
            if os.path.samefile(file_path, fq_control_path):
                return

            if re.findall(control_pattern, file_path):
                return

            # Do not operate on already-filtered files
            if 'filtered' in file_path:
                return

            # IDK why this is necessary?
            if file_path in files_done:
                return

            files_done.append(file_path)

            # Load file into FreqFile object
            contents: s.FreqFile = s.load_frequency_file(file_path)

            # Apply Brownian filter
            dropped, remaining = contents.filter(f.sls_threshold_filter,
                                                sls_threshold=threshold)

            total_dropped += dropped
            total_remaining += remaining

            if remaining == 0:
                files_skipped.append(file_path)
                return

            # Save as modified file
            contents.save_tracks(file_path + '.filtered.csv')

        # Call our function which operates on each file
        s.for_each_file(filter_single_file, dir_path, r'.*track.*\.csv')

    try:
        # Call our function which operates on each directory
        s.for_each_dir(filter_folder, root)

    finally:

        if total_dropped + total_remaining:
            percentage_dropped: float = total_dropped / (total_dropped
                                                        + total_remaining)
            percentage_dropped *= 100.0
            percentage_dropped = round(percentage_dropped, 5)

            print(f'Of {total_dropped + total_remaining}, dropped {total_dropped}',
                f'({percentage_dropped}%)',
                f'with k = {k}')

        else:
            print('ERROR: No points were loaded!')

        if files_skipped:
            print('Overfiltering caused the skippage of',
                  f'{len(files_skipped)} files out of {len(files_done)}')
            print('Skipped files:')

            for file in files_skipped:
                print(f'\t{file}')

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
