'''
Turns more formal Speckle CSV files into the kind recognized by
these scripts.
Jordan Dehmel, 2024
'''

import sys
from typing import List, Dict, Tuple
import pandas as pd


HEADER: str = '#speckles csv ver 1.2\n#x(double)	y(double)	size(double)	frame(int)	type(int)\n'
START_SPECKLE: str = '#%start speckle%\n'
STOP_SPECKLE: str = '#%stop speckle%\n'


def main(args: List[str]) -> int:
    '''
    Takes two command line args: The file to parse and the
    location to save it at.
    '''

    if len(args) != 3:
        print(
            'Takes two command line args: The formal CSV '
            'speckle file to parse and the location to save '
            'the adapted regular TSV speckle file at.')

        return 1

    # Extract filename to fix and save location
    src: str = args[1]
    dest: str = args[2]
    print(f'Converting from {src} to {dest}...')

    # Load the source file (full on CSV)
    loaded_src: pd.DataFrame = pd.read_csv(src)

    # Ensure valid source
    assert set(loaded_src.keys()) == set(['speckle_id', 'x', 'y', 'size', 'frame'])

    # Maps speckle_id to a list of (x, y, frame)
    speckles: Dict[int, List[Tuple[float, float, int]]] = {}

    # Parse useful info
    for _, row in loaded_src.iterrows():
        speckle_id: int = int(row['speckle_id'])
        x: float = float(row['x'])
        y: float = float(row['y'])
        frame: int = int(row['frame'])

        # NOTE: The source format is 0-indexed, while the target format is 1-indexed
        frame = frame + 1

        if speckle_id not in speckles:
            speckles[speckle_id] = []

        speckles[speckle_id].append((x, y, frame))

    # Sort by frame
    for _, value in speckles.items():
        value.sort(key=lambda t: t[2])

    # Reformat
    with open(dest, 'w', encoding='UTF-8') as output_file:
        # Write speckle header
        output_file.write(HEADER)

        # For each unique speckle ID
        for _, value in speckles.items():
            # Begin speckle
            output_file.write(START_SPECKLE)

            # Write frames
            for x, y, frame in value:
                output_file.write(f'{x}\t{y}\t{frame}\n')

            # End speckle
            output_file.write(STOP_SPECKLE)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
