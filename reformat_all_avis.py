'''
Reformat all *.avi files recursively in the specified directory.
Unless you know what you're doing, you do not want to modify
anything outside of the `settings` section.
'''

import os
import sys
import shutil
from typing import List
from speckle import speckle

################################################################
# Begin Settings
################################################################

#speckle.original_w = 1192   # The original width of the video
#speckle.processed_w = 256   # The target width of the video
speckle.encoding = 'mjpeg'   # The (ImageJ compatible) encoding

# Note: The output will also be converted to black and white.

################################################################
# End Settings
################################################################


def main(args: List[str]) -> int:
    '''
    Reformats all *.avi files recursively in the specified
    directory.

    :param args: The command-line arguments passed.
    :returns: 0 upon success, error code upon failure.
    '''

    if len(args) != 3:
        raise ValueError('Exactly two command line arguments must be provided:',
            'The place to save output, and the folder to operate on.')

    # A constant folder to copy all avi files to after formatting.
    # The names will be mangled when pasted here for disambiguation.
    backup_avi_folder = args[1]

    def reformat_avi_file(what: str) -> None:
        '''
        The function which operates on a single *.avi file. This
        will create the file 'out.avi'.

        :param what: The filepath to operate on.
        :returns: Nothing.
        '''

        # Skip files which have already been done
        if '_rf.avi' in what:
            return

        # Recurse if directory
        if os.path.isdir(what):
            speckle.for_each_file(reformat_avi_file, what, r'.*\.avi')
            return

        print(f'Operating on file {what}')

        # Downsize, grayscale, and re-encode the given file.
        # Saves w/ a `_rf.avi` suffix for `reformatted`.
        speckle.reformat_avi(what, what + '_rf.avi')

        # This includes the fully-qualified system path of a file
        # in its copied name, allowing disambiguation later on.
        # This is called both "mangling" and "name disambiguation".
        mangled_name: str = what.replace(
            ' ', '_').replace('/', '_').replace('\\', '_').lower()

        # Copy the mangled name to the backup folder.
        shutil.copy(what + '_rf.avi', backup_avi_folder +
                    '/' + mangled_name)

    # Run w/ given parameters
    speckle.for_each_file(reformat_avi_file, args[2], r'.*\.avi')

    # Return 0, indicating no error.
    return 0


# Run the script
if __name__ == '__main__':
    sys.exit(main(sys.argv))
