import speckle
import sys
import os

if __name__ == '__main__':

    from_filepath: str = sys.argv[1]
    to_filepath: str = ''

    if len(sys.argv) == 3:
        to_filepath = sys.argv[2]
    elif len(sys.argv) == 2:
        to_filepath = from_filepath.replace('_speckles.csv', '_tracks.csv')

    print(f'Processing speckle file {from_filepath} to tracks file {to_filepath}...')

    speckle.process_file(
        from_filepath,
        '/tmp/junk.csv',
        to_filepath,
        speckle.original_w / speckle.processed_w)

'''
set FOLDER bot
python speckle_to_track.py ~/data/120um_16v_speckles_clean/$FOLDER/analysis/100khz_speckles.csv &&
python speckle_to_track.py ~/data/120um_16v_speckles_clean/$FOLDER/analysis/75khz_speckles.csv &&
python speckle_to_track.py ~/data/120um_16v_speckles_clean/$FOLDER/analysis/50khz_speckles.csv &&
python speckle_to_track.py ~/data/120um_16v_speckles_clean/$FOLDER/analysis/25khz_speckles.csv &&
python speckle_to_track.py ~/data/120um_16v_speckles_clean/$FOLDER/analysis/10khz_speckles.csv &&
python speckle_to_track.py ~/data/120um_16v_speckles_clean/$FOLDER/analysis/5khz_speckles.csv &&
python speckle_to_track.py ~/data/120um_16v_speckles_clean/$FOLDER/analysis/1khz_speckles.csv &&
python speckle_to_track.py ~/data/120um_16v_speckles_clean/$FOLDER/analysis/control_speckles.csv
'''
