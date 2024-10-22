'''
This will rescale all values in a speckle file by some constant
coefficient. It will first verify that the given expected width
is a valid descriptor of the file (no points fall outside it,
and it is not the case that all points fall inside one quarter
section of it).

Jordan Dehmel, 2024
jdehmel@outlook.com
'''

import os
import sys
from io import StringIO
from typing import Set, Tuple, List
import pandas as pd
import speckle as s


validated: Set[Tuple[str, int]] = set()


def approx_eq(l: float, r: float) -> bool:
    '''
    Returns true iff abs(l - r) < TOLERANCE
    '''

    if l != l or r != r:
        print('Warning! NaN encountered!')
        return True

    diff: float = abs(l - r)

    if diff < 0.0001:
        return True

    print(f'abs({l} - {r}) = {diff}')
    return False


def validate_dimensions_for_data(filepath: str,
                                 old_w: int) -> None:
    '''
    Asserts that the given dimensions accurately describe the
    data. If this is not the case, throws an error.
    '''

    assert old_w > 0

    data_falls_outside_quartile: bool = False

    # Load input
    text: str = ''
    with open(filepath, 'rb') as file:
        text = file.read().decode()

    # Process
    text = text.replace('\t', ',')
    text = text.replace('\n', ',\n')

    while ',,' in text:
        text = text.replace(',,', ',')

    # Load data
    frame: pd.DataFrame = pd.read_csv(StringIO(text))

    is_first: bool = True
    for row in frame.iterrows():
        if is_first:
            is_first = False
            continue

        if 'stop speckle' in row[0][0]:
            continue

        if 'start speckle' in row[0][0]:
            continue

        # cur_track.append(
        #     float(row[0][0]),  # x
        #     float(row[0][1]),  # y
        #     int(row[0][2]))    # t (unused here)

        x: float = float(row[0][0])
        y: float = float(row[0][1])

        assert x <= old_w, 'Invalid old dimension!'
        assert y <= old_w, 'Invalid old dimension!'
        assert x >= 0.0, 'Invalid old dimension!'
        assert y >= 0.0, 'Invalid old dimension!'

        if x * 2.0 > old_w or y * 2.0 > old_w:
            data_falls_outside_quartile = True

    assert data_falls_outside_quartile, \
        'Too large of a description!'

    validated.add((filepath, old_w))


def adjust_file(input_filepath: str,
                output_filepath: str,
                old_w: int,
                new_w: int) -> None:
    '''
    RUN VALIDATION BEFORE THIS!
    '''

    output_text: str = ''

    # Write the following:
    output_text += '#speckles csv ver 1.2\n'
    output_text += '#x(double)\ty(double)\tsize(double)\t' + \
        'frame(int)\ttype(int)\n'

    assert (input_filepath, old_w) in validated, \
        'Cannot adjust unvalidated data'
    assert new_w > old_w
    assert new_w > 0

    coefficient: float = new_w / old_w

    # Load input
    text: str = ''
    with open(input_filepath, 'rb') as file:
        text = file.read().decode()

    # Process
    text = text.replace('\t', ',')
    text = text.replace('\n', ',\n')

    while ',,' in text:
        text = text.replace(',,', ',')

    # Load data
    frame: pd.DataFrame = pd.read_csv(StringIO(text))

    is_first: bool = True
    for row in frame.iterrows():
        if is_first:
            is_first = False
            continue

        if 'stop speckle' in row[0][0]:
            output_text += '#%stop speckle%\n'
            continue

        if 'start speckle' in row[0][0]:
            output_text += '#%start speckle%\n'
            continue

        # cur_track.append(
        #     float(row[0][0]),  # x
        #     float(row[0][1]),  # y
        #     int(row[0][2]))    # t (unused here)

        x_old: float = float(row[0][0])
        y_old: float = float(row[0][1])
        t: int = int(row[0][2])

        x: float = x_old * coefficient
        y: float = y_old * coefficient

        assert x <= new_w
        assert y <= new_w
        assert x >= 0.0
        assert y >= 0.0

        assert approx_eq(y * (old_w / new_w), y_old)
        assert approx_eq(x * (old_w / new_w), x_old)

        output_text += f'{x}\t{y}\t{t}\n'

    with open(output_filepath, 'w', encoding='utf-8') as file:
        file.write(output_text)


def validate_and_adjust_file(inp_fp: str,
                             out_fp: str,
                             inp_w: int,
                             out_w: int) -> None:
    '''
    Validates the input data, adjusts it to the output filepath,
    then validates the output dataTuple. If any of these steps
    fail, an assertion error will be thrown.
    '''

    try:
        validate_dimensions_for_data(inp_fp, out_w)
        print(f'SKIPPING FILE {inp_fp}, as it is already at',
              f'{out_w}p')
        return
    except AssertionError:
        pass

    # Ensure good data going in
    validate_dimensions_for_data(inp_fp, inp_w)
    before_tracks: s.FreqFile = \
        s.load_frequency_file(inp_fp, 'speckles')

    # Adjust the file
    adjust_file(inp_fp, out_fp, inp_w, out_w)

    # Ensure the output was good
    validate_dimensions_for_data(out_fp, out_w)
    after_tracks: s.FreqFile = \
        s.load_frequency_file(out_fp, 'speckles')

    # Assert scaling factors affected tracks in the correct way
    assert approx_eq(before_tracks.sls_mean()
                     * (out_w / inp_w), after_tracks.sls_mean())
    assert approx_eq(before_tracks.sls_std()
                     * (out_w / inp_w), after_tracks.sls_std())

    # Update user
    print(f'Rescaled from {inp_fp} at {inp_w}p to',
          f'{out_fp} at {out_w}p')


def main(argv: List[str]) -> int:
    '''
    Main function.
    '''

    print('Speckle rescalar. This may take a very long time, '
          'due to the extensive validation it does. This takes',
          'either 1 command line argument (the folder) or 3',
          '(the folder, the input pixel width, and the output',
          'pixel width).\n')

    inp_w: int = 256
    out_w: int = 1192

    # Load from args
    assert len(argv) in (2, 4), \
        'Please provide 1 or 3 arguments.'
    folder: str = argv[1]

    if len(argv) == 4:
        inp_w = int(argv[2])
        out_w = int(argv[3])

    print(f'Reformatting files from {inp_w}p to {out_w}p in',
          f'folder {folder}.')

    assert input('Is this okay (if so, type "YES, DO IT"): ') \
        == 'YES, DO IT', 'Aborting...'

    count: int = 0
    def rescale_wrapper(inp_fp: str) -> None:
        '''
        Rescale the given file
        '''

        nonlocal count

        # Recurse if this is a directory
        if os.path.isdir(inp_fp):
            s.for_each_file(rescale_wrapper, inp_fp)
            return

        # Ignore non-csv files
        if inp_fp[-4:] != '.csv':
            return

        # Otherwise, adjust this file
        try:
            validate_and_adjust_file(inp_fp,
                                     inp_fp,
                                     inp_w,
                                     out_w)
            count += 1

        except AssertionError:
            pass

    print(f'Operating on folder {folder}...')
    s.for_each_file(rescale_wrapper, folder)
    print(f'Reformatted {count} speckle files.')

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
