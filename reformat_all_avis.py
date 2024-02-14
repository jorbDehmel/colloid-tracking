'''
Reformat all *.avi files recursively in the specified directory.
'''

import sys
import shutil
from typing import List
from speckle import speckle

# A constant folder to copy all avi files to after formatting.
# The names will be mangled when pasted here for disambiguation.
BACKUP_AVI_FOLDER: str = '/home/jorb/Programs/physicsScripts/dump'


def main(args: List[str]) -> int:
    '''
    Reformats all *.avi files recursively in the specified
    directory.

    :param args: The command-line arguments passed.
    :returns: 0 upon success, error code upon failure.
    '''

    def reformat_avi_file(what: str) -> None:
        '''
        The function which operates on a single *.avi file. This
        will create the file 'out.avi'.

        :param what: The filepath to operate on.
        :returns: Nothing.
        '''

        if '_rf.avi' in what:
            return

        # speckle.reformat_avi(what, what + '_rf.avi')

        if BACKUP_AVI_FOLDER:

            mangled_name: str = what.replace(
                ' ', '_').replace('/', '_').replace('.', '_').lower() + '.avi'

            shutil.copy(what + '_rf.avi', BACKUP_AVI_FOLDER +
                        '/' + mangled_name)

    if len(args) > 1:
        speckle.for_each_file(reformat_avi_file, args[1], r'.*\.avi')
    else:
        raise RuntimeError('No working directory was provided.')

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
