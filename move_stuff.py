import os
import sys
import shutil


if __name__ == '__main__':

    for root, dirs, files in os.walk('.'):
        for file in files:
            if '/' not in root:
                continue

            to: str = root[root.index('/') + 1:] + '.csv'
            to = to.replace(' ', '').lower()

            print(f'Copying from {root}/{file} to {to}')
            shutil.copyfile(root + '/' + file, to)
