'''
Entry script for simplifying the process
'''

import sys
import os
from typing import List
from shutil import rmtree

import reformat_all_avis
import rescale_speckles
import speckle_to_track
import speckle_filterer
import speckle_graphing
import comparisons
import speckle_const_sls_filter
import collate_without_graphing


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
        print('Cannot run on non-POSIX system! This means ' +
              'that you are running on Windows and not a ' +
              'UNIX shell: Please install Windows Subsystem ' +
              'for Linux (WSL). Then try again from within a ' +
              'WSL shell.\n' +
              'https://learn.microsoft.com/en-us/windows/wsl' +
              '/install')
        return -128

    if os.system('ffmpeg -version > /dev/null') != 0:
        print('Missing package "ffmpeg". Please use your ' +
              'local package manager to install it.')
        return -256

    where_to_operate: str = input('Path to folder: ')
    where_to_operate = os.path.realpath(where_to_operate)

    assert os.path.exists(where_to_operate)
    assert os.path.isdir(where_to_operate)

    have_tracked: bool = input(
        'Have speckle files already been extracted? [y/n] '
    ).lower() == 'y'

    if not have_tracked:
        # Reformat AVIs
        print('This will ensure a script-friendly naming ' +
              'scheme, then reformat all raw AVI files.')
        print('Note: Running this on already-formatted files ' +
              'will have no effect.\n')

        # Make everything (recursively) lowercase
        # (Embarrassingly brute-force way.
        # Turn your head, anyone who respects me)
        for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            cmd: str = (f'find {where_to_operate} -depth ' +
                        f'-iname "*{c}*" -exec rename --all "{c}" ' +
                        f'"{c.lower()}" "{{}}" \\;')
            assert os.system(cmd) == 0

        # Remove spaces
        assert os.system(
            f'find {where_to_operate} -depth -iname "* *" ' +
            '-exec rename --all " " "" {} \\;') == 0

        save_location: str = '/tmp/reformat_all_avis/'

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
            # Delete originals
            os.system(f'find {where_to_operate} -type f ' +
                      '-iname "*.avi" -not -iname "*_rf.avi" ' +
                      '-exec rm -f "{}" \\;')

            # Rename reformatted files to be originals
            os.system(f'find {where_to_operate} -type f ' +
                      '-iname "*_rf.avi" ' +
                      '-exec rename "_rf.avi" "" "{}" \\;')

        print('\nDone with preprocessing. Please use ' +
              'SpeckleTrackerJ to analyze the videos, then ' +
              'run the other half of this script.')

    else:
        # Rescale speckles
        print('Rescaling speckles...')
        try:
            assert rescale_speckles.main(
                ['', where_to_operate]) == 0
        except AssertionError:
            print('WARNING: Rescaling exited with error!')

        # Convert to tracks
        print('Converting speckles to tracks...')
        assert speckle_to_track.main(
            ['', where_to_operate]) == 0

        # Filter tracks
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
                print('No filter could be applied; Halting.')
                return -512

        # Simple extraction, before complicated version
        print('Collating and saving means and stds...')
        try:
            collate_without_graphing.main(
                ['', where_to_operate,
                 where_to_operate + '/filtered_means.csv',
                 r'.*(filtered|control.*)\.csv'])
            collate_without_graphing.main(
                ['', where_to_operate,
                 where_to_operate + '/all_means.csv', ''])
            print('Means and stds have been collated.')
        except Exception as e:
            print(e)
            print('Warning: Failed to collate info')

        if input('Graph? [y/N]: ').lower()[0] != 'y':
            print('Exiting without graphing.')
            return 0

        os.chdir(where_to_operate)

        # Local graphs
        voltage_dirs: List[str] = \
            [f for f in os.listdir() if os.path.isdir(f)]

        for voltage_dir in voltage_dirs:
            os.chdir(where_to_operate)

            # Create graphs
            assert speckle_graphing.main(
                ['', voltage_dir, '.*',
                 '.*(filtered|control).*']) == 0

            assert comparisons.main(
                ['', voltage_dir, voltage_dir,
                 '.*(filtered|control).*']) == 0

            # Organize graphs
            if not os.path.exists(f'{voltage_dir}/graphs/'):
                os.mkdir(f'{voltage_dir}/graphs/')

            assert os.system(
                f'mv *.csv *.png {voltage_dir}/graphs/') == 0

            # Rename graphs
            all_items: List[str] = \
                os.listdir(f'{voltage_dir}/graphs')

            common_prefix: str = os.path.commonprefix(all_items)

            assert os.system(
                f'find {voltage_dir}/graphs -type f -exec ' +
                f'rename "{common_prefix}" "" {{}} \\;') == 0

        assert comparisons.main(
            ['', '.', '.', '.*(filtered|control).*']) == 0

        # Organize graphs
        if not os.path.exists('graphs'):
            os.mkdir('graphs')

        assert os.system('mv *.csv *.png graphs/') == 0

        # Rename graphs
        all_items: List[str] = os.listdir('graphs')

        common_prefix: str = os.path.commonprefix(all_items)

        assert os.system(
            'find graphs -type f -exec rename ' +
            f'"{common_prefix}" "" {{}} \\;') == 0

    return 0


if __name__ == '__main__':
    sys.exit(main())
