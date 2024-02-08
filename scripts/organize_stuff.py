'''
Built to go through folders and cut off junk prefixes from all
filenames, then organize them into neat folders.
'''

import os
import sys
import shutil


def main() -> int:
    '''
    Main function
    '''

    for root, _, files in os.walk('.'):
        for file in files:
            if '/' not in root:
                continue

            if 'clean_' in file:
                trunc: str = file[file.index('clean_') + 6:]

                if 'track_scatter' in trunc:
                    trunc = trunc.replace('track_scatter', '')
                if 'track_data_summary' in trunc:
                    trunc = trunc.replace('track_data_summary', '')

                trunc = root + '/' + trunc

                if os.path.exists(trunc):
                    print(f'Cannot overwrite file {trunc}')
                    continue

                print(f'From {root}/{file} to {trunc}')
                shutil.move(root + '/' + file, trunc)

            if '_*_' in file:
                new_name: str = root + '/' + file.replace('_*_', '')

                print(f'From {root}/{file} to {new_name}')
                shutil.move(root + '/' + file, new_name)


if __name__ == '__main__':
    sys.exit(main())
