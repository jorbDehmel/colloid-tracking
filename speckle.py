'''
Attempts to read a speckle csv file

The output speckle tracker produces is not an actual .csv file,
so it needs a bit of preprocessing first. Just replace the tabs
and newlines with commas and erase some lines at the beginning
and it should be fine.
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


input_filepath: str = 'speckles.csv'
original_w: int = 1028
processed_w: int = 256


if __name__ == '__main__':
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
    plt.show()

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
    plt.show()

    print(f'Mean SLS: {sls_mean} processed pixels/frame, SLS STD: {sls_std} processed pixels/frame')
    
    if original_w is not None:
        print(f'Mean SLS: {(original_w / processed_w) * sls_mean} pixels/frame, SLS STD: {(original_w / processed_w) * sls_std} pixels/frame')
