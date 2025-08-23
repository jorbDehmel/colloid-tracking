'''
Loads a series of SPECKLE files, then notes the MSD over time
for every track therein. Output files will have the header:

```csv
id,x,y,frame,msd
```

Each particle will be found within.
'''

from typing import List, Dict, Tuple
import sys
import speckle
from matplotlib import pyplot as plt
import pandas as pd


def main(args: List[str]) -> int:
    '''
    Main fn to be called by importers or as a script
    '''

    if len(args) != 2:
        print(
            'Please provide a path to search for speckles in.')
        return 1

    path: str = args[1]

    # Discover all the (unfiltered) speckle files
    files: List[str] = []

    def check_file(where: str) -> None:
        if where.endswith('_speckles.csv'):
            files.append(where)

    speckle.for_each_file(check_file, folder=path)

    print('The collated data will include all and only these files:')
    for file in files:
        print(file)

    assert input('OK? [y/N] ') == 'y'

    # This is where we will save our data
    headers: List[str] = ['file', 'track_id', 'frame', 'msd']
    data: List[Tuple[str, int, int, float]] = []

    # Iterate over files
    for file_i, file in enumerate(files):
        print(f'On {file_i} of {len(files)}')

        # Load
        tracks: List[speckle.Track] = speckle.load_tracks(file)

        # Iterate over tracks
        for track_id, track in enumerate(tracks):
            # Create a new dummy track w/ empty spots
            partial_track: speckle.Track = speckle.Track([], [], [])

            # For each spot in track, gradually append and note
            # MSD
            for x, y, frame in zip(track.x_values, track.y_values, track.frames):
                # Append this spot
                partial_track.append(x, y, frame)

                # Log MSD
                msd: float = partial_track.msd()
                data.append((file, track_id, frame, msd))

    # Save as csv
    print(f'Saving {len(data)} data points...')
    pd.DataFrame(data, columns=headers).to_csv('msd_by_time.csv')

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
