'''
Resources for reading and processing speckle files.
Also functions as a main function processing a single speckle
output file.
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

        return self.frames[-1] - self.frames[0]

    def displacement(self) -> float:
        '''
        Straight line distance from first to last point
        '''

        dx: float = self.x_values[-1] - self.x_values[0]
        dy: float = self.y_values[-1] - self.y_values[0]
        distance: float = (dx ** 2 + dy ** 2) ** 0.5

        return distance


input_filepath: str = 'speckles.csv'
original_w: int = 1028
processed_w: int = 256


def process_file(in_filepath: str, spots_filepath: str,
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

        # Process into array
        arr: List[List[Union[str, float, int]]] = []
        cur: List[Union[str, float, int]] = []

        '''
        Real header from trackMate:

        LABEL,TRACK_INDEX,TRACK_ID,NUMBER_SPOTS,NUMBER_GAPS,NUMBER_SPLITS,NUMBER_MERGES,NUMBER_COMPLEX,LONGEST_GAP,TRACK_DURATION,TRACK_START,TRACK_STOP,TRACK_DISPLACEMENT,TRACK_X_LOCATION,TRACK_Y_LOCATION,TRACK_Z_LOCATION,TRACK_MEAN_SPEED,TRACK_MAX_SPEED,TRACK_MIN_SPEED,TRACK_MEDIAN_SPEED,TRACK_STD_SPEED,TRACK_MEAN_QUALITY,TOTAL_DISTANCE_TRAVELED,MAX_DISTANCE_TRAVELED,CONFINEMENT_RATIO,MEAN_STRAIGHT_LINE_SPEED,LINEARITY_OF_FORWARD_PROGRESSION,MEAN_DIRECTIONAL_CHANGE_RATE
        Label,Track index,Track ID,Number of spots in track,Number of gaps,Number of split events,Number of merge events,Number of complex points,Longest gap,Track duration,Track start,Track stop,Track displacement,Track mean X,Track mean Y,Track mean Z,Track mean speed,Track max speed,Track min speed,Track median speed,Track std speed,Track mean quality,Total distance traveled,Max distance traveled,Confinement ratio,Mean straight line speed,Linearity of forward progression,Mean directional change rate
        Label,Index,ID,N spots,N gaps,N splits,N merges,N complex,Lgst gap,Duration,Track start,Track stop,Track disp.,Track X,Track Y,Track Z,Mean sp.,Max speed,Min speed,Med. speed,Std speed,Mean Q,Total dist.,Max dist.,Cfn. ratio,Mn. v. line,Fwd. progr.,Mn. ? rate
        ,,,,,,,,,(frame),(frame),(frame),(pixel),(pixel),(pixel),(pixel),(pixel/frame),(pixel/frame),(pixel/frame),(pixel/frame),(pixel/frame),(quality),(pixel),(pixel),,(pixel/frame),,(rad/frame)
        
        1 real header row, followed by 3 dumb header rows

        Important header items:

        TRACK_INDEX,TRACK_DURATION,TRACK_DISPLACEMENT,MEAN_STRAIGHT_LINE_SPEED,

        '''

        labels: List[str] = ['TRACK_INDEX', 'TRACK_DURATION', 'TRACK_DISPLACEMENT', 'MEAN_STRAIGHT_LINE_SPEED']

        # And 3 dummy rows (see above)
        dummy: List[str] = ['_' for _ in labels]
        arr.append(dummy)
        arr.append(dummy)
        arr.append(dummy)

        # Followed by real track data
        for i, track in enumerate(tracks):
            cur = [i,
                   track.duration() * adjustment_coefficient,
                   track.displacement() * adjustment_coefficient,
                   track.sls() * adjustment_coefficient]

            arr.append(cur)

        # Save as csv
        df: pd.DataFrame = pd.DataFrame(arr, columns=labels)
        df.to_csv(tracks_filepath)


if __name__ == '__main__':
    # Uncomment to demonstrate translation script for speckle data to tracks data
    # process_file('speckles.csv', 'junk.csv', 'junk_tracks.csv', original_w / processed_w)

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
            cur_track.append(float(row[0][0]), float(row[0][1]), int(row[0][2]))

        i += 1

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

    plt.scatter(x_values, y_values, c=colors, s=3.0)
    plt.title('Tracked Speckles')
    plt.savefig('tracked_speckles.png')
    # plt.show()

    plt.clf()

    plt.scatter([i for i in range(len(tracks))],
                [track.sls() for track in tracks],
                c='r', label='Mean Straight Line Speed')
    plt.scatter([i for i in range(len(tracks))],
                [track.mdts() for track in tracks],
                c='b', label='Mean Distance Traveled Speed')
    plt.scatter([i for i in range(len(tracks))],
                [track.mv() for track in tracks],
                c='g', label='Mean Instantaneous Velocity')

    sls_values: List[float] = [track.sls() for track in tracks]
    sls_mean: float = sum(sls_values) / len(sls_values)
    sls_std: float = np.std(sls_values)

    plt.hlines(y=[sls_mean - sls_std, sls_mean, sls_mean + sls_std], xmin=0, xmax=len(tracks), colors=['k'], label='Mean SLS +- 1 STD')

    plt.legend()
    plt.title('Speckle Velocities')
    plt.savefig('speckle_velocities.png')
    # plt.show()

    print(f'Mean SLS: {sls_mean} processed pixels/frame, SLS STD: {sls_std} processed pixels/frame')
    
    if original_w is not None:
        print(f'Mean SLS: {(original_w / processed_w) * sls_mean} pixels/frame, SLS STD: {(original_w / processed_w) * sls_std} pixels/frame')
