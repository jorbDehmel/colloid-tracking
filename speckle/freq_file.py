'''
Defines the class FreqFile, which encompasses a set of tracks.
Also keeps track of the source file and the pattern used to find
it. This module also defines the BasicTrack class, which is a
track loaded from a "Tracks"-formatted csv file, rather than a
"speckle"-formatted one.

Jordan Dehmel, 2024
jedehmel@mavs.coloradomesa.edu
jdehmel@outlook.com
'''

from typing import List, Optional, Union, Dict, Protocol, Any, Tuple
import pandas as pd
import numpy as np
from speckle.speckle import Track


class BasicTrack:
    '''
    A track as loaded from a "tracks"-formatted `csv` file.

    Has index, duration, displacement, and SLS. The use of index
    is inadvisable, since this is an arbitrary measure and
    probably does not contain meaningful information. This class
    is designed to share important methods with the Track class.
    '''

    def __init__(self,
                 duration: int,
                 displacement: float,
                 sls: float,
                 msd: float) -> None:
        '''
        Setup a BasicTrack object with the given parameters.
        '''

        self.__duration = duration
        self.__displacement = displacement
        self.__sls = sls
        self.__msd = msd

    def sls(self) -> float:
        '''
        :returns: The SLS value for this track.
        '''

        return self.__sls

    def msd(self) -> float:
        '''
        :returns: The mean-squared displacement for this track.
        '''

        return self.__msd

    def displacement(self) -> float:
        '''
        :returns: The track displacement.
        '''

        return self.__displacement

    def duration(self) -> int:
        '''
        :returns: The number of frames that the track existed
            for.
        '''

        return self.__duration


class FilterFunction(Protocol):
    '''
    A type denoting a valid filtering function.
    '''

    def __call__(self,
                 track: Union[Track, BasicTrack],
                 **kwargs: Any) -> bool:
        pass


def speckle_filter(fn: FilterFunction) -> FilterFunction:
    '''
    Decorator for type checking. This will fail if the decorated
    function is not a valid Filterfunction.
    '''

    return fn


class FreqFile:
    '''
    A file from a single frequency. Has a set of tracks, as well
    as some data about what was used to find it.
    '''

    def __init__(self,
                 tracks: Optional[List[Union[Track, BasicTrack]]] = None,
                 path: Optional[str] = None,
                 pattern: Optional[str] = None,
                 label: Optional[str] = None,
                 tags: Optional[List[str]] = None) -> None:
        '''
        Initialize a frequency file.
        '''

        self.tracks: List[Union[Track, BasicTrack]] = tracks if tracks else []
        self.erased: List[Union[Track, BasicTrack]] = []
        self.path: str = path if path else ''
        self.pattern: str = pattern if pattern else ''
        self.frequency_label: str = label if label else ''
        self.tags: List[str] = tags if tags else []

    def save_tracks(self, where: str) -> None:
        '''
        Save this object as a tracks.csv file.

        :param where: The filepath to save at.
        '''

        # Construct dictionary
        d: Dict[str, List[Any]] = {}
        dummy: List[Any] = ['_', '_', '_']

        d['TRACK_INDEX'] = dummy + [i for i, _ in enumerate(self.tracks)]
        d['TRACK_DURATION'] = dummy + [track.duration()
                                       for track in self.tracks]
        d['TRACK_DISPLACEMENT'] = dummy + [track.displacement()
                                           for track in self.tracks]
        d['MEAN_STRAIGHT_LINE_SPEED'] = dummy + [track.sls()
                                                 for track in self.tracks]

        # Construct DataFrame
        df: pd.DataFrame = pd.DataFrame(d)

        # Save as csv
        df.to_csv(where)

    def __repr__(self) -> str:
        '''
        Return a str representation of this object.

        :returns: A string representing this object.
        '''

        out: str = self.path + f'\nw/ tags: {self.tags}\nsls\tdisp\tdur\n'

        for track in self.tracks:
            out += f'{track.sls()}\t{track.displacement()}' + \
                   f'\t{track.duration()}\n'

        out += f'(Plus {len(self.erased)} erased tracks)'

        return out

    def restore_erased(self) -> None:
        '''
        Restore all items from erased.
        '''

        self.tracks += self.erased
        self.erased = []

    def purge_erased(self) -> List[Union[Track, BasicTrack]]:
        '''
        Clear the cache of erased tracks and return them.

        :returns: The erased tracks. This is discardable if you
            don't need it.
        '''

        to_return = self.erased[:]
        self.erased = []

        return to_return

    def filter(self,
               whether_to_remove: FilterFunction,
               **kwargs: Any) -> Tuple[int, int]:
        '''
        Filters the tracks according to the given function. The
        list of tracks is iterated over, and any track for which
        `whether_to_remove(track)` is `True` is moved to the
        erased track list.

        :param whether_to_remove: A lambda filter function.
        :returns: A 2-tuple which is (number erased, number
            remaining).
        '''

        new_tracks: List[Union[Track, BasicTrack]] = []
        erased: int = 0

        for track in self.tracks:
            if whether_to_remove(track, **kwargs):
                self.erased.append(track)
                erased += 1
            else:
                new_tracks.append(track)

        self.tracks = new_tracks

        return (erased, len(self.tracks))

    def msd_mean(self) -> float:
        '''
        :returns: The mean of the MSD values of the tracks
            within.
        '''

        msd_values: List[float] = [track.msd() for track in self.tracks]
        return float(np.mean(msd_values))

    def msd_std(self) -> float:
        '''
        :returns: The std of the MSD values of the tracks
            within.
        '''

        msd_values: List[float] = [track.msd() for track in self.tracks]
        return float(np.std(msd_values))

    def sls_mean(self) -> float:
        '''
        Returns the mean SLS of the tracks.

        :returns: The mean of the SLS's of the tracks within.
        '''

        sls_values: List[float] = [track.sls() for track in self.tracks]
        return float(np.mean(sls_values))

    def sls_std(self) -> float:
        '''
        Returns the SLS standard deviation of the tracks.

        :returns: The STD of the SLS's of the tracks within.
        '''

        sls_values: List[float] = [track.sls() for track in self.tracks]
        return float(np.std(sls_values))


def load_frequency_file(path: str,
                        file_format: str = 'tracks',
                        pattern: Optional[str] = None,
                        label: Optional[str] = None) -> FreqFile:
    '''
    Loads a given `csv` file into a FreqFile object. The target
    file should be in the "tracks" format. The return object is
    easily filterable.

    :param path: The path to the csv file to load.
    :returns: A FreqFile object with the given data.
    '''

    out: FreqFile = FreqFile(path=path, pattern=pattern, label=label)

    # Load a "track"-formatted file.
    if file_format == 'tracks':

        # Load initial dataframe
        tracks: pd.DataFrame = pd.read_csv(path)

        # Trim garbage rows
        tracks.drop([0, 1, 2], inplace=True)

        # Iterate over rows
        for row in tracks.iterrows():

            # Get relevant series
            row = row[1]

            # Setup default values for if these keys are not
            # present
            duration: int = -1
            displacement: float = -1.0
            sls: float = -1.0
            msd: float = -1.0

            # Check for each key's presence in the row, and if
            # it is there, use that value.
            if 'TRACK_DURATION' in row:
                duration = int(row['TRACK_DURATION'])

            if 'TRACK_DISPLACEMENT' in row:
                displacement = float(row['TRACK_DISPLACEMENT'])

            if 'MEAN_STRAIGHT_LINE_SPEED' in row:
                sls = float(row['MEAN_STRAIGHT_LINE_SPEED'])

            if 'MEAN_SQUARED_DISPLACEMENT' in row:
                msd = float(row['MEAN_SQUARED_DISPLACEMENT'])

            # Construct BasicTrack with read params
            to_append: BasicTrack = BasicTrack(duration,
                                               displacement,
                                               sls,
                                               msd)

            # Append this data
            out.tracks.append(to_append)

    # Load a "speckle"-formatted file.
    else:
        raise NotImplementedError('Loading a Speckle file has not'
                                  + 'been implemented yet.')

    return out
