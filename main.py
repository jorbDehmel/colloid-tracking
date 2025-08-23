'''
Entry script for simplifying the process
'''

import sys
import os
from typing import List, Callable
import shutil
from shutil import rmtree
import subprocess

import reformat_all_avis
import rescale_speckles
import speckle_to_track
import speckle_filterer
import speckle_graphing
import comparisons
import speckle_const_sls_filter
import collate_without_graphing
import msd_by_time

from speckle import for_each_file, for_each_dir


def move(src: str, dest: str) -> None:
    '''
    Move from some source file to some destination file
    '''

    if src == dest:
        return

    try:

        if os.path.isdir(dest):
            dest = os.path.join(dest, os.path.basename(src))

        if os.path.exists(dest):
            if os.path.isdir(dest):
                rmtree(dest)
            else:
                os.remove(dest)

        shutil.move(src, dest)

    except:
        print(f'Failed to move {src} to {dest}')


def main() -> int:
    '''
    :param v: CLI args
    :returns: 0 on success, nonzero on failure
    '''

    # Print information
    print('This is a script for pre- and post-processing of\n' +
          'speckle-tracked data. It should be run before\n' +
          'analysis to ready the data for processing and\n' +
          'after analysis to create track files, apply\n' +
          'Brownian filtering, and produce graphs. In\n' +
          'theory, no other scripts should be necessary\n' +
          'when using this one.\n\n' +
          'Jordan Dehmel, 2023-2025\n' +
          'Colorado Mesa University\n')

    # Do system checks
    if os.name != 'posix':
        print('Warning: Not designed to run on non-POSIX ' +
              'system! This means that you are running on ' +
              'Windows and not a UNIX shell: Please install ' +
              'Windows Subsystem for Linux (WSL). Then try ' +
              'again from within a WSL shell. If you ' +
              'continue on Windows, this script may not ' +
              'work.\n\n'
              'https://learn.microsoft.com/en-us/windows/wsl' +
              '/install\n\n')

    where_to_operate: str = input('Path to folder: ')
    where_to_operate = os.path.realpath(where_to_operate)

    assert os.path.exists(where_to_operate)
    assert os.path.isdir(where_to_operate)

    have_tracked: bool = input(
        'Have speckle files already been extracted? [y/N] '
    ).lower() == 'y'

    if not have_tracked:
        # Reformat AVIs
        print('This will ensure a script-friendly naming ' +
              'scheme, then reformat all raw AVI files.')
        print('Note: Running this on already-formatted files ' +
              'will have no effect.\n')

        if subprocess.run(
                ['ffmpeg', '-version'],
                stdout=None, stderr=None).returncode != 0:
            print('Missing package "ffmpeg". Please use your ' +
                  'local package manager to install it. If ' +
                  'an error occurred, this is the reason!')

        save_location: str = 'reformat_all_avis'

        if not os.path.exists(save_location):
            os.mkdir(save_location)

        print('Calling `reformat_all_avis.py`...')

        res: int = reformat_all_avis.main(
            ['reformat_all_avis.py', save_location,
             where_to_operate])

        rmtree(save_location)

        if res != 0:
            return res

        do_erase: bool = input(
            'Replace originals w/ formatted? [y/n] '
        ).lower() == 'y'

        if do_erase:
            # Delete originals and rename reformatted files to
            # be the originals
            def remove_and_replace(fp: str) -> None:
                if fp.endswith('.avi') and not \
                        fp.endswith('_rf.avi'):
                    move(fp, fp.replace('_rf.avi', ''))
            for_each_file(remove_and_replace, where_to_operate)

        print('\nDone with preprocessing. Please use ' +
              'SpeckleTrackerJ to analyze the videos, then ' +
              'run the other half of this script.')

    else:
        # Rescale speckles
        if input('Rescale speckles? [y/N]: ').lower() == 'y':
            print('Rescaling speckles...')
            try:
                assert rescale_speckles.main(
                    ['', where_to_operate]) == 0
            except AssertionError:
                print('WARNING: Rescaling exited with error!')

        # Convert to tracks
        if input('Convert to tracks? [y/N]: ').lower() == 'y':
            print('Converting speckles to tracks...')
            assert speckle_to_track.main(
                ['', where_to_operate]) == 0

        # Filter tracks
        if input('Filter tracks? [y/N]: ').lower() == 'y':
            print('Filtering tracks...')
            filter_res: int = speckle_filterer.main(
                ['', where_to_operate])

            if filter_res != 0:
                print('Potentially lethal filtering error(s) ' +
                      'occurred! Please check log!')

                do_const_sls_filter: bool = input(
                    'Apply constant SLS filter instead of ' +
                    'Brownian? [y/n] ').lower() == 'y'

                if do_const_sls_filter:
                    threshold: float = float(
                        input('SLS threshold: '))

                    assert speckle_const_sls_filter.main(
                        ['', where_to_operate, threshold]) == 0

                else:
                    print(
                        'No filter could be applied.')

        # Simple extraction, before complicated version
        if input('Collate all data? [y/N]: ').lower()[0] == 'y':
            print('Collating and saving means and stds...')

            collate_without_graphing.main(
                ['', where_to_operate,
                    os.path.join(
                        where_to_operate, 'filtered_means.csv'),
                    r'.*(filtered|control.*)\.csv'])
            collate_without_graphing.main(
                ['', where_to_operate,
                    os.path.join(
                        where_to_operate, 'all_means.csv'),
                    r'.*(filtered|control.*)\.csv'])
            print('Means and stds have been collated.')

        # MSD by time log
        if input('Save MSD by time file? [y/N]: ').lower()[0] == 'y':
            print('Saving MSD by time file...')

            msd_by_time.main(['', where_to_operate])

            print('Finished logging MSD by time.')

        if input('Graph? [y/N]: ').lower()[0] != 'y':
            print('Exiting without graphing.')
            return 0

        os.chdir(where_to_operate)

        # Local graphs
        voltage_dirs: List[str] = \
            [f for f in os.listdir() if os.path.isdir(f)]

        for voltage_dir in voltage_dirs:
            if voltage_dir == 'graphs':
                continue

            print(f'On voltage dir {voltage_dir}...')
            old_dir = os.getcwd()
            os.chdir(voltage_dir)

            # Organize graphs
            if not os.path.exists('graphs'):
                os.mkdir('graphs')

            # Create graphs
            try:
                speckle_graphing.main(
                    ['', '.', '.*',
                    '.*(filtered|control).*'])
            except:
                print('Failed to graph (pt 1)!')

            try:
                assert comparisons.main(
                    ['', '.', '.',
                    '.*(filtered|control).*']) == 0
            except:
                print('Failed to graph (pt 2)!')

            if not os.path.exists('graphs'):
                os.mkdir('graphs')

            for f in os.listdir():
                if f.endswith('.csv') or f.endswith('.png'):
                    move(f, 'graphs')

            # Rename graphs
            all_items: List[str] = os.listdir('graphs')

            common_prefix: str = os.path.commonprefix(all_items)

            def remove_common_prefix(fp: str) -> None:
                '''
                Removes the common prefix from the given filepath
                '''

                if fp != fp.replace(common_prefix, ''):
                    move(fp, fp.replace(common_prefix, ''))

            if common_prefix:
                for_each_file(remove_common_prefix)

            os.chdir(old_dir)

        try:
            assert comparisons.main(
                ['', '.', '.', '.*(filtered|control).*']) == 0
        except:
            print('Failed to graph (pt 3)')

        # Organize graphs
        if not os.path.exists('graphs'):
            os.mkdir('graphs')

        for f in os.listdir():
            if f.endswith('.csv') or f.endswith('.png'):
                move(f, 'graphs')

        # Rename graphs
        all_items = os.listdir('graphs')

        common_prefix = os.path.commonprefix(all_items)

        def remove_common_prefix(fp: str) -> None:
            '''
            Removes the common prefix from the given filepath
            '''

            move(fp, fp.replace(common_prefix, ''))

        for_each_file(remove_common_prefix)

    print('Done!')

    return 0


if __name__ == '__main__':
    sys.exit(main())
