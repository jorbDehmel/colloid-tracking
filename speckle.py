'''
Resources for reading and processing speckle files.
Also functions as a main function processing a single speckle
output file.

Statistic details:

Mean Straight Line Speed = magnitude(vector from start to end) / number of frames
Mean Instantaneous Velocity = sum(magnitude(velocities)) / number of velocities
Mean Distance Traveled Speed = sum(magnitude(velocities)) / number of frames

Capable of dropping any speckle track w/ duration under a
certain threshold if so desired.

'''

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from typing import *

class Track:
    def __init__(self, x: List[float] = [], y: List[float] = [], f: List[float] = []):
        self.x_values: List[float] = x[:]
        self.y_values: List[float] = y[:]
        self.frames: List[int] = f[:]

    def append(self, x: float, y: float, t: int) -> None:
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
        dx: List[float] = [self.x_values[i + 1] - self.x_values[i] for i in range(len(self.x_values) - 1)]
        dy: List[float] = [self.y_values[i + 1] - self.y_values[i] for i in range(len(self.y_values) - 1)]

        # Create distance traveled list
        assert len(dx) == len(dy)
        distances: List[float] = [(dx[i] ** 2 + dy[i] ** 2) ** 0.5 for i in range(len(dx))]
        
        # Number of frames it existed
        df: int = self.frames[-1] - self.frames[0] + 1
        
        return sum(distances) / df

    def mv(self) -> float:
        '''
        Mean of the magnitude of the velocity vectors
        '''

        if len(self.frames) < 2:
            return 0.0

        # Create delta lists
        dx: List[float] = [self.x_values[i + 1] - self.x_values[i] for i in range(len(self.x_values) - 1)]
        dy: List[float] = [self.y_values[i + 1] - self.y_values[i] for i in range(len(self.y_values) - 1)]

        # Create distance traveled list
        assert len(dx) == len(dy)
        distances: List[float] = [(dx[i] ** 2 + dy[i] ** 2) ** 0.5 for i in range(len(dx))]
        
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


'''
Used for pixel resizing later. Change if these are not the
dimensions of the data.

original_w is the width in pixels of the source footage.
processed_w is the width in pixels of the speckle-tracked footage.
These may be different, as downsizing the footage for speckle tracking
significantly improves speed.
'''
original_w: int = 1028
processed_w: int = 256

'''
If set to 0, does no duration thresholding. Otherwise,
automatically drops any track w/ frame duration less than this
value.
'''
duration_threshold: int = 30


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
    with open(spots_filepath, 'w') as file:
        file.write(text)

    # If requested, save tracks
    if tracks_filepath is not None:

        # Load data
        frame: pd.DataFrame = pd.read_csv(spots_filepath)
    
        tracks: List[Track] = []
        cur_track: Track = Track()
        i: int = 0

        for row in frame.iterrows():
            if i == 0:
                i += 1
                continue

            if 'stop speckle' in row[0][0]:
                tracks.append(cur_track)
            elif 'start speckle' in row[0][0]:
                cur_track = Track()
            else:
                cur_track.append(float(row[0][0]), float(row[0][1]), int(row[0][2]))

            i += 1

        # Remove tracks below the duration threshold
        tracks = [track for track in tracks if track.duration() >= duration_threshold]

        # Process into array
        arr: List[List[Union[str, float, int]]] = []
        cur: List[Union[str, float, int]] = []

        labels: List[str] = ['TRACK_INDEX', 'TRACK_DURATION', 'TRACK_DISPLACEMENT', 'MEAN_STRAIGHT_LINE_SPEED']

        # And 3 dummy rows (see above)
        dummy: List[str] = ['_' for _ in labels]
        arr.append(dummy)
        arr.append(dummy)
        arr.append(dummy)

        # Followed by real track data
        for i, track in enumerate(tracks):
            cur = [i,
                   track.duration(),
                   track.displacement() * adjustment_coefficient,
                   track.sls() * adjustment_coefficient]

            arr.append(cur)

        # Save as csv
        df: pd.DataFrame = pd.DataFrame(arr, columns=labels)
        df.to_csv(tracks_filepath)


if __name__ == '__main__':
    # Uncomment to demonstrate translation script for speckle data to tracks data
    process_file('/home/jorb/data/120um_16v_speckles_clean/bot/analysis/1khz_speckles.csv', 'junk.csv', 'junk_tracks.csv', original_w / processed_w)
    input_filepath = 'junk.csv'

    frame: pd.DataFrame = pd.read_csv(input_filepath)
    
    tracks: List[Track] = []
    cur_track: Track = Track()
    i: int = 0

    for row in frame.iterrows():
        if i == 0:
            i += 1
            continue

        if 'stop speckle' in row[0][0]:
            tracks.append(cur_track)
        elif 'start speckle' in row[0][0]:
            cur_track = Track()
        else:
            cur_track.append(float(row[0][0]), processed_w - float(row[0][1]), int(row[0][2]))

        i += 1

    # Load old stuff from trackmate
    old_x: List[float] = []
    old_y: List[float] = []
    old_sls: List[float] = []
    trackmate_filepath: str = 'filtered track data.csv'

    old: pd.DataFrame = pd.read_csv(trackmate_filepath)
    for i, row in enumerate(old.iterrows()):
        if i < 3:
            continue

        old_x.append(float(row[1]['TRACK_X_LOCATION']))
        old_y.append(float(row[1]['TRACK_Y_LOCATION']))
        old_sls.append(float(row[1]['MEAN_STRAIGHT_LINE_SPEED']))

    # Adjust scale
    old_x = [i / (original_w / processed_w) for i in old_x]
    old_y = [i / (original_w / processed_w) for i in old_y]
    old_sls = [i / (original_w / processed_w) for i in old_sls]

    # Adjust position (y is flipped)
    old_y = [processed_w - i for i in old_y]

    all_colors: List[str] = ['b', 'g', 'r', 'y']

    x_values: List[float] = []
    y_values: List[float] = []
    colors: List[str] = []

    for j, track in enumerate(tracks):
        for i in range(len(track.x_values)):
            x_values.append(track.x_values[i])
            y_values.append(track.y_values[i])

            colors.append(all_colors[j % len(all_colors)])

    print(f'Processed {len(tracks)} tracks with {sum([len(track.x_values) for track in tracks])} data points')

    plt.xlim((0, processed_w))
    plt.ylim((0, processed_w))


    plt.scatter(old_x, old_y, s=25.0, label='TrackMate Starting Positions')
    
    plt.scatter(old_x, old_y, s=25.0, label='TrackMate Starting Positions')
    plt.scatter(x_values, y_values, c=colors, s=3.0)

    lgd = plt.legend(bbox_to_anchor=(1.1, 1.05))

    plt.title('Tracked Speckles (Scaled Down)')
    plt.xlabel('X Pixels')
    plt.ylabel('Y Pixels')
    plt.savefig('tracked_speckles.png', bbox_extra_artists=(lgd,), bbox_inches='tight')
    
    plt.clf()

    '''
    dx = dy = sqrt(2) * sls
    '''

    old_arrows: List[Tuple[float, float, float]] = []
    new_arrows: List[Tuple[float, float, float]] = []

    for track in tracks:
        new_arrows.append((track.x_values[0], track.y_values[0], track.sls()))

    for i in range(len(old_sls)):
        old_arrows.append((old_x[i], old_y[i], old_sls[i]))

    for arrow in old_arrows:
        plt.arrow(arrow[0], arrow[1], 100 * arrow[2], 0)

    for arrow in new_arrows:
        plt.arrow(arrow[0], arrow[1], 100 * arrow[2], 0)

    plt.scatter(x_values, y_values, c=colors, s=3.0, alpha=0.1)

    plt.scatter(old_x, old_y, s=25.0, label='TrackMate')
    plt.scatter([track.x_values[0] for track in tracks], [track.y_values[0] for track in tracks], s=25.0, label='Speckles')

    plt.legend()
    plt.savefig('vectors.png')

    plt.clf()

    # Sort things
    old_sls.sort(reverse=True)
    tracks.sort(reverse=True, key=lambda x: x.sls())

    plt.scatter([i for i in range(len(tracks))],
                [track.sls() for track in tracks],
                c='r', label='Mean Straight Line Speed (Speckles)')

    plt.scatter([i for i in range(len(old_sls))],
                [sls for sls in old_sls],
                c='b', label='Mean Straight Line Speed (Manual)')

    error_squared: List[float] = [abs(tracks[i].sls() - old_sls[i]) for i in range(min(len(tracks), len(old_sls)))]
    plt.scatter([i for i in range(len(error_squared))],
                [err for err in error_squared],
                c='y', label='Absolute Value of Error')

    '''
    plt.scatter([i for i in range(len(tracks))],
                [track.mdts() for track in tracks],
                c='b', label='Mean Distance Traveled Speed')
    plt.scatter([i for i in range(len(tracks))],
                [track.mv() for track in tracks],
                c='g', label='Mean Instantaneous Velocity')
    '''

    sls_values: List[float] = [track.sls() for track in tracks]
    sls_mean: float = sum(sls_values) / len(sls_values)
    sls_std: float = np.std(sls_values)

    plt.hlines(y=[sls_mean - sls_std, sls_mean, sls_mean + sls_std], xmin=0, xmax=len(tracks), colors=['k'], label='Mean SLS +- 1 STD')
    
    manual_mean: float = sum(old_sls) / len(old_sls)
    manual_std: float = np.std(old_sls)

    plt.hlines(y=[manual_mean - manual_std, manual_mean, manual_mean + manual_std], xmin=0, xmax=len(tracks), colors=['r'], label='Manual Mean SLS +- 1 STD')

    plt.legend()
    plt.title('Speckle Velocities')
    plt.savefig('speckle_velocities.png')

    print(f'Mean SLS: {sls_mean} processed pixels/frame, SLS STD: {sls_std} processed pixels/frame')
    
    if original_w is not None:
        print(f'Mean SLS: {(original_w / processed_w) * sls_mean} pixels/frame, SLS STD: {(original_w / processed_w) * sls_std} pixels/frame')
