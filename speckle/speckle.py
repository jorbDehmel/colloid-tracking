'''
Resources for reading and processing speckle files.
Also functions as a main function processing a single speckle
output file.

Statistic details:

Mean Straight Line Speed = magnitude(vector from start to end)
                           / number of frames
Mean Instantaneous Velocity = sum(magnitude(velocities))
                              / number of velocities
Mean Distance Traveled Speed = sum(magnitude(velocities))
                               / number of frames

Capable of dropping any speckle track w/ duration under a
certain threshold if so desired.
'''

from re import match
import os
import subprocess
from typing import List, Union, Callable, Tuple
from numpy import hypot
import pandas as pd


class Track:
    '''
    A class representing a track of a speckle-tracked particle.
    This is the type of Track loaded from a "speckles"-formatted
    `csv` file- That is to say, NOT a "tracks" file. There is a
    similar class for "tracks" files in `./freq_file.py`.
    '''

    def __init__(self, x: List[float], y: List[float], f: List[int]):
        self.x_values: List[float] = x[:]
        self.y_values: List[float] = y[:]
        self.frames: List[int] = f[:]

    def append(self, x: float, y: float, t: int) -> None:
        '''
        Append a given point from speckle tracker
        '''

        self.x_values.append(x)
        self.y_values.append(y)
        self.frames.append(t)

    def sls(self) -> float:
        '''
        Returns the mean straight line speed
        '''

        if len(self.frames) < 2:
            return 0.0

        dx: float = self.x_values[-1] - self.x_values[0]
        dy: float = self.y_values[-1] - self.y_values[0]
        distance: float = (dx ** 2 + dy ** 2) ** 0.5

        # Number of frames
        df: int = self.frames[-1] - self.frames[0]

        return distance / df

    def mdts(self) -> float:
        '''
        Returns the mean distance traveled speed
        '''

        if len(self.frames) < 2:
            return 0.0

        # Create delta lists
        dx: List[float] = [self.x_values[i + 1] - self.x_values[i]
                           for i in range(len(self.x_values) - 1)]
        dy: List[float] = [self.y_values[i + 1] - self.y_values[i]
                           for i in range(len(self.y_values) - 1)]

        # Create distance traveled list
        assert len(dx) == len(dy)
        distances: List[float] = [
            (dx[i] ** 2 + dy[i] ** 2) ** 0.5 for i in range(len(dx))]

        # Number of frames
        df: int = self.frames[-1] - self.frames[0]

        return sum(distances) / df

    def mv(self) -> float:
        '''
        Mean of the magnitude of the velocity vectors
        '''

        if len(self.frames) < 2:
            return 0.0

        # Create delta lists
        dx: List[float] = [self.x_values[i + 1] - self.x_values[i]
                           for i in range(len(self.x_values) - 1)]
        dy: List[float] = [self.y_values[i + 1] - self.y_values[i]
                           for i in range(len(self.y_values) - 1)]

        # Create distance traveled list
        assert len(dx) == len(dy)
        distances: List[float] = [
            (dx[i] ** 2 + dy[i] ** 2) ** 0.5 for i in range(len(dx))]

        return sum(distances) / len(distances)

    def duration(self) -> int:
        '''
        Number of frames the track existed for
        '''

        return self.frames[-1] - self.frames[0] + 1

    def displacement(self) -> float:
        '''
        Straight line distance from first to last point
        '''

        dx: float = self.x_values[-1] - self.x_values[0]
        dy: float = self.y_values[-1] - self.y_values[0]
        distance: float = (dx ** 2 + dy ** 2) ** 0.5

        return distance

    def msd(self) -> float:
        '''
        Return the mean squared displacement for this particle.

        :returns: The mean-squared displacement of the particle.
        '''

        # Compute displacements as a list
        displacements: List[float] = []

        first_x: float = self.x_values[0]
        first_y: float = self.y_values[0]

        # Easier iteration
        zipped: List[Tuple[float, float]] = [
            (self.x_values[i], self.y_values[i])
            for i, _ in enumerate(self.frames)
        ]

        for x, y in zipped[1:]:

            dx: float = x - first_x
            dy: float = y - first_y

            distance: float = hypot(abs(dx), abs(dy))

            displacements.append(distance)

        print(displacements)

        # Compute sum of squares of that list
        sos: float = sum(d ** 2 for d in displacements)

        # Return that sum divided by the number of displacements
        return sos / len(displacements)


# Used for pixel resizing later. Change if these are not the
# dimensions of the data.
# original_w is the width in pixels of the source footage.
# processed_w is the width in pixels of the speckle-tracked footage.
# These may be different, as downsizing the footage for speckle tracking
# significantly improves speed.
original_w: int = 1028
processed_w: int = 256

encoding: str = 'mjpeg'

# If set to 0, does no duration thresholding. Otherwise,
# automatically drops any track w/ frame duration less than this
# value.
duration_threshold: int = 0


def for_each_file(apply: Callable[[str], None],
                  folder: str = '.',
                  matching: str = '.*') -> None:
    '''
    For each file recursively in `folder` which
    matches the given RegEx `matching`, apply the given
    function.

    :param apply: The function / lambda to call on a match.
    :param folder: The folder to recursively walk.
    :param matching: The RegEx pattern which designates a match.
    '''

    visited: List[str] = []

    # Walk all files recursively in the current directory
    for root, _, files in os.walk(folder):

        # For each file (not directory) in the cwd
        for file in files:

            full_name: str = os.path.realpath(root + '/' + file)

            if match(matching, full_name) and full_name not in visited:
                apply(full_name)
                visited.append(full_name)


def for_each_dir(apply: Callable[[str], None],
                 folder: str = '.',
                 matching: str = '.*') -> None:
    '''
    For each directory recursively in `folder` which
    matches the given RegEx `matching`, apply the given
    function.

    :param apply: The function / lambda to call on a match.
    :param folder: The folder to recursively walk.
    :param matching: The RegEx pattern which designates a match.
    '''

    visited: List[str] = []

    # Walk all files recursively in the current directory
    for root, dirnames, _ in os.walk(folder):

        # For each directory in the cwd
        for dir_name in dirnames:

            full_name: str = os.path.realpath(root + '/' + dir_name)

            if match(matching, full_name) and full_name not in visited:
                apply(full_name)
                visited.append(full_name)


def reformat_avi(to_format_filepath: str,
                 save_filepath: str = 'out.avi') -> None:
    '''
    Uses `ffmpeg` to re-encode and downscale a given
    avi file for compatability w/ speckle tracker. This should
    be used on all avi files before analysis to avoid long wait
    times.

    :param to_format_filepath: The input avi file to process.
    :param save_filepath: The place to save the file after
        processing.
    '''

    assert to_format_filepath[-4:] == '.avi'
    assert save_filepath[-4:] == '.avi'

    # Run command to encode and downscale the given file,
    # with the output being saved at the desired location.
    subprocess.run([
        'ffmpeg', '-y', '-i', to_format_filepath, '-c:v', encoding,
        '-vf', 'scale=-2:' + str(processed_w), save_filepath
    ], check=True)

    print(f'File {to_format_filepath} was re-encoded as mjpeg and',
          f'resized to {processed_w} pixels,',
          f'with the result saved at {save_filepath}')


def process_file(input_filepath: str, spots_filepath: str,
                 tracks_filepath: Union[str, None] = None,
                 adjustment_coefficient: float = 1.0) -> None:
    '''
    Performs preprocessing on speckle output files to put them
    into real .csv format.

    :param in_filepath: The filepath to process from
    :param spots_filepath: The filepath to save to when done as
        a spots file.
    :param tracks_filepath: The filepath (or None) to as a
        tracks file.
    :param adjustment_coefficient: The amount that the loaded
        file should be scaled up in order for the values to
        match the original file.
    '''

    # Load input
    text: str = ''
    with open(input_filepath, 'rb') as file:
        text = file.read().decode()

    # Process
    text = text.replace('\t', ',')
    text = text.replace('\n', ',\n')
    text = text.replace(',,', ',')

    # Save spots
    with open(spots_filepath, 'w', encoding='utf8') as file:
        file.write(text)

    # If requested, save tracks
    if tracks_filepath is not None:

        # Load data
        frame: pd.DataFrame = pd.read_csv(spots_filepath)

        tracks: List[Track] = []
        cur_track: Track = Track([], [], [])

        is_first: bool = True
        for row in frame.iterrows():
            if is_first:
                is_first = False
                continue

            if 'stop speckle' in row[0][0]:
                tracks.append(cur_track)
            elif 'start speckle' in row[0][0]:
                cur_track = Track([], [], [])
            else:
                cur_track.append(float(row[0][0]), float(
                    row[0][1]), int(row[0][2]))

        # Remove tracks below the duration threshold
        tracks = [track for track in tracks if track.duration() >=
                  duration_threshold]

        # Process into array
        arr: List[List[Union[str, float, int]]] = []
        cur: List[Union[str, float, int]] = []

        labels: List[str] = ['TRACK_INDEX', 'TRACK_DURATION',
                             'TRACK_DISPLACEMENT', 'MEAN_STRAIGHT_LINE_SPEED']

        # And 3 dummy rows (see above)
        dummy: List[Union[str, float, int]] = ['_' for _ in labels]
        arr.append(dummy)
        arr.append(dummy)
        arr.append(dummy)

        # Followed by real track data
        for k, cur_track in enumerate(tracks):
            cur = [k,
                   cur_track.duration(),
                   cur_track.displacement() * adjustment_coefficient,
                   cur_track.sls() * adjustment_coefficient]

            arr.append(cur)

        # Save as csv
        df: pd.DataFrame = pd.DataFrame(arr, columns=labels)
        df.to_csv(tracks_filepath)
