'''
Quick and dirty script to move files. Useful during the cleaning
of poorly-human-formatted data into uniform script-analyzable
data. See commenting in main function for more details.
'''

import os
import sys
import shutil


def main() -> int:
    '''
    Main function. Targets all nested *.csv files in the cwd,
    moves them down one subfolder and cleans their names. This
    is useful ONLY for `analysis/` subfolders.
    '''

    # Walk all files recursively in the current directory
    for root, _, files in os.walk('.'):

        # For each file (not directory) in the cwd
        for file in files:

            # If in root, do not do anything. This only targets
            # nested files.
            if '/' not in root:
                continue

            # We only want to target *.csv files for some operations
            if '.csv' in file:

                # Create a target filepath which is one directory
                # down from here.
                to: str = root[root.index('/') + 1:] + '.csv'

                # Remove all spaces and turn the filepath lowercase.
                to = to.replace(' ', '').lower()

                # Update user on what is to be done.
                print(f'Copying from {root}/{file} to {to}')

                # Copy the file from the original location to the
                # new location.
                shutil.copyfile(root + '/' + file, to)

    return 0


if __name__ == '__main__':
    # Call the main function and exit
    sys.exit(main())
