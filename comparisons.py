'''
Makes some comparisons by voltage and frequency for height-wise
data.

All graphs produced herein should be velocity vs. height.

Does this process for each pattern, searching for files ONLY
in the current working directory.

Jordan Dehmel, 2023 - present
jedehmel@mavs.coloradomesa.edu
jdehmel@outlook.com
'''

import sys
import re
from typing import List, Dict, Tuple
import pandas as pd
from matplotlib import pyplot as plt

import speckle


# The set of all possible chamber heights. A set of files should
# match only one.
z_position_filters: List[str] = [r'8940', r'8960', r'8965', r'8980', r'8985',
                                 r'8990', r'9010', r'9015', r'9035', r'9040',
                                 r'9060', r'9080', r'9090', r'9115', r'9140',
                                 r'9180', r'9197', r'9205', r'9230', r'9240',
                                 r'9255', r'9265', r'9280', r'9290', r'9305',
                                 r'9315', r'9340',
                                 r'top-195', r'top-165', r'top-135',
                                 r'top-100', r'top-97', r'top-75', r'top-50',
                                 r'top-25', r'top(?!-)', r'bot(?!\+)',
                                 r'bot\+25', r'bot\+50', r'bot\+70',
                                 r'bot\+75', r'bot\+100', r'bot\+135',
                                 r'bot\+165', r'bot\+190', r'bot\+195',
                                 r'bot\+210']

# The voltage filters to use
voltages: Dict[str, str] = {r'(?<!1)5[_ ]?[vV]': '5v',
                            r'7[_ ]?[vV]': '7v',
                            r'8[_ ]?[vV]': '8v',
                            r'9[_ ]?[vV]': '9v',
                            r'10[_ ]?[vV]': '10v',
                            r'12[_ ]?[vV]': '12v',
                            r'15[_ ]?[vV]': '15v',
                            r'16[_ ]?[vV]': '16v',
                            r'20[_ ]?[vV]': '20v'}
skip_voltage: bool = False

# The frequency filters to use
control_pattern: str = r'control[0-9]*_tracks\.csv'
frequencies: Dict[str, str] = {
    control_pattern: '0khz',
    r'0\.5khz[0-9]*': '0.5khz',
    r'0\.2khz[0-9]*': '0.2khz',
    r'0\.3khz[0-9]*_tracks\.csv': '0.3khz',
    r'0\.4khz[0-9]*_tracks\.csv': '0.4khz',
    r'0\.8khz[0-9]*': '0.8khz',
    r'1khz[0-9]*': '1khz',
    r'2khz[0-9]*': '2khz',
    r'(?<![\.0-9])3khz[0-9]*': '3khz',
    r'(?<![\.0-9])5khz[0-9]*': '5khz',
    r'10khz[0-9]*': '10khz',
    r'25khz[0-9]*': '25khz',
    r'50khz[0-9]*': '50khz',
    r'75khz[0-9]*': '75khz',
    r'100khz[0-9]*': '100khz'}


def clean_pattern(what: str, replacement: str = '_', exclude: str = '') -> str:
    '''
    Cleans a pattern of any gross symbols.

    :param what: The pattern to clean.
    :param replacement: The thing to replace bad characters
        with.
    :param exclude: Any characters to allow.
    :returns: The cleaned pattern.
    '''

    garbage: str = './\\^$*?<!'
    for c in exclude:
        garbage = garbage.replace(c, '')

    out: str = what

    out = re.sub(r'\(.*\)', '', out)
    out = re.sub(r'\[.*\]', '', out)
    out = re.sub(r'\{.*\}', '', out)

    for c in garbage:
        out = out.replace(c, replacement)

    return out


def graph_each_frequency(root: str,
                         saveat: str = '.',
                         pattern: str = '.*') -> None:
    '''
    Graphs by each frequency in `root`.

    :param root: The folder to use as the root directory for
        these operations.
    '''

    column_name: str = 'MEAN_STRAIGHT_LINE_SPEED'
    all_data: Dict[str, Tuple[List[str], List[float], List[float]]] = {}

    # Used for comparing SLS and MSD
    all_sls: List[float] = []
    all_msd: List[float] = []

    # Iterate over frequency patterns
    for frequency in frequencies:

        print(f'Frequency {clean_pattern(frequency, "")}')

        means: Dict[str, float] = {}
        stds: Dict[str, float] = {}
        title: str = ''

        def do_single_frequency_file(file: str) -> None:
            '''
            Loads a single frequency's tracks file and loads the
            mean and std for straight line speed. Appends this
            information to external variables.

            :param file: The file to operate on.
            '''

            nonlocal means, stds, title, all_sls, all_msd

            # Skip non-matching
            if not re.findall(pattern, file) or 'ANOMALY' in file or not file.endswith('.csv') or '/graphs/' in file:
                print(f'Rejected file {file}')
                return

            print(f'Accepted file {file}')
            title = file

            # Load tracks file
            tracks: pd.DataFrame = pd.read_csv(file)
            tracks.drop([0, 1, 2], inplace=True)

            speeds = tracks[column_name].astype(float)

            if 'MEAN_SQUARED_DISPLACEMENT' in tracks:
                all_sls += list(speeds)
                all_msd += list(tracks['MEAN_SQUARED_DISPLACEMENT'].astype(float))
            else:
                print('Failed to find MSD entries.')

            # Calculate mean MEAN_STRAIGHT_LINE_SPEED
            mean: float = speeds.mean()

            # Calculate std MEAN_STRAIGHT_LINE_SPEED
            std: float = speeds.std()

            # Extract friendlier chamber height label for the
            # graph x-axis
            label: str = file
            for height_pattern in z_position_filters:

                if re.findall(height_pattern, file):
                    label = height_pattern
                    break

            if label in means or label in stds:
                print(f'Abandoning {file}')
                return

            # Append to `means` and `stds`
            means[label] = mean
            stds[label] = std

        # Fetch all the data from the current frequency pattern
        speckle.for_each_file(do_single_frequency_file, root, '.*' + frequency)

        if len(means) == 0:
            print(f'Skipping pattern {frequency}')
            continue

        # Fetch the list of keys in ascending order. This will
        # be used several times later on.
        keys: List[str] = list(means)
        keys.sort(key=z_position_filters.index)

        cleaned_keys = [clean_pattern(key, '') for key in keys]

        # Graph the fetched data (this is a single frequency, by
        # chamber height)
        plt.clf()

        plt.title(clean_pattern(frequency) + f'\n{title}')
        plt.xlabel('Chamber Height')
        plt.ylabel('Mean Straight Line Speed')

        plt.plot(cleaned_keys, [means[key] for key in keys], label=clean_pattern(frequency))
        plt.errorbar(x=cleaned_keys,
                 y=[means[key] for key in keys],
                 yerr=[stds[key] for key in keys])

        plt.legend()
        plt.savefig(saveat + '/'
                    + clean_pattern(frequency, '', '.')
                    + '_chamber_height.png')

        plt.close()

        all_data[frequency] = (cleaned_keys,
                               [means[key] for key in keys],
                               [stds[key] for key in keys])

        # Save as csv file
        pd.DataFrame(data={
            'HEIGHT': cleaned_keys,
            'MEAN_STRAIGHT_LINE_SPEED': [means[key] for key in keys],
            'STRAIGHT_LINE_SPEED_STD': [stds[key] for key in keys],
        }).to_csv(saveat + '/'
            + clean_pattern(frequency, '', '.')
            + '_chamber_height.csv')

    plt.clf()

    plt.title(title)
    plt.xlabel('Chamber Height')
    plt.ylabel('Mean Straight Line Speed')

    for frequency, (cleaned_keys, means, stds) in all_data.items():
        plt.errorbar(x=cleaned_keys,
                     y=means,
                     yerr=stds,
                     label=clean_pattern(frequency))

    plt.legend(bbox_to_anchor=(1,1), loc="upper left")
    plt.savefig(saveat + '/chamber_height.png', bbox_inches='tight')

    plt.close()


def main(argv: List[str]) -> int:
    '''
    Main function
    :param argv: CLI args
    :returns: 0 on success, nonzero on failure
    '''

    if len(argv) != 4:
        print('Please provide a root folder, a destination folder,',
              'and a file-matching pattern.',
              '(The root folder should contain heightwise subfolders)')
        sys.exit(1)

    graph_each_frequency(argv[1], argv[2], argv[3])

    sys.exit(0)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
