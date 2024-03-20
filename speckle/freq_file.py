'''
Defines the class FreqFile, which encompasses a set of tracks.
Also keeps track of the source file and the pattern used to find
it.

Jordan Dehmel, 2024
jedehmel@mavs.coloradomesa.edu
jdehmel@outlook.com
'''

from typing import List, Optional
from speckle import Track


class FreqFile:
    '''
    A file from a single frequency. Has a set of tracks, as well
    as some data about what was used to find it.
    '''

    def __init__(self, tracks: Optional[Track] = None,
                 path: Optional[str] = None,
                 pattern: Optional[str] = None,
                 label: Optional[str] = None) -> None:
        '''
        Initialize a frequency file.
        '''

        self.tracks: List[Track] = tracks if tracks else []
        self.path: str = path if path else ''
        self.pattern: str = pattern if pattern else ''
        self.frequency_label: str = label if label else ''
