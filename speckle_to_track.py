'''
Operates recursively on the given directory, transforming all
`_speckles.csv` files into `_tracks.csv` files.

Jordan Dehmel, 2024
jdehmel@outlook.com
jedehmel@mavs.coloradomesa.edu
'''

import sys
import speckle


# Note: This is a very important filter! It's not a good idea to
# turn it off.
speckle.duration_threshold = 30


def main() -> int:
    '''
    Main function for use when this is called as a script
    '''

    if len(sys.argv) == 1:
        print('Please provide 1 command-line argument: The folder to operate in.')
        return 1

    from_filepath: str = sys.argv[1]

    def convert_file(name: str) -> None:
        '''
        Converts a single file from speckles to tracks.
        '''

        print(f'On file {name}')

        try:
            to_filepath: str = name.replace('_speckles.csv', '_tracks.csv')
            speckle.process_file(
                name,
                '/tmp/junk.csv',
                to_filepath,
                speckle.original_w / speckle.processed_w)
        except:
            print(f'Failure in {name}')
            raise

    speckle.for_each_file(convert_file, from_filepath, r'.*_speckles\.csv')

    return 0


if __name__ == '__main__':
    sys.exit(main())
