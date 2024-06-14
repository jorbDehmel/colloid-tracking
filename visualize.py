'''
Visualizes speckle files.
'''

import sys
from typing import List
from matplotlib import pyplot as plt
import speckle as s


def viz_file(filepath: str) -> None:
    '''
    Visualizes a single file
    '''

    file: s.FreqFile = \
        s.load_frequency_file(filepath, 'speckles')

    xs: List[float] = []
    ys: List[float] = []
    lengths: List[int] = []

    flip: bool = True
    flip_max_pixels: int = 1192

    for track in file.tracks:

        assert isinstance(track, s.Track)
        lengths.append(track.duration())

        for x, y in zip(track.x_values, track.y_values):

            if flip:
                y = flip_max_pixels - y

            xs.append(x)
            ys.append(y)

    print(f'File {filepath}:')
    print(f'Mean SLS: {file.sls_mean()}')
    print(f'SLS std:  {file.sls_std()}\n')

    plt.title(filepath)
    plt.scatter(xs, ys, 1.0)
    plt.show()

    plt.close()


def main() -> None:
    '''
    Main function
    '''

    assert len(sys.argv) != 1, 'Please provide at least 1 file.'

    for filepath in sys.argv[1:]:
        viz_file(filepath)


if __name__ == '__main__':
    main()
