'''
Some essential filters for the speckle package.

Jordan Dehmel, 2024
jedehmel@mavs.coloradomesa.edu
jdehmel@outlook.com
'''

from typing import Union, Dict, Any
import speckle as s
from speckle import speckle_filter


class OverFilteringError(RuntimeError):
    '''
    An error class to be raised when a filter results in too few
    remaining items.
    '''


@speckle_filter
def sls_threshold_filter(track: Union[s.Track, s.BasicTrack],
                         **kwargs: Any) -> bool:
    '''
    Returns true if the given track should be removed by the
    Brownian filter. Expects a definition for 'sls_threshold' in
    kwargs.

    :param track: The track in question.
    :param kwargs: Additional keyword arguments.
    :returns: True if this track should be removed, False
        if it should be kept.
    '''

    keywords: Dict[str, Any] = kwargs
    assert 'sls_threshold' in keywords, 'Must provide `threshold` as a kwarg'
    sls_threshold: float = keywords['sls_threshold']

    # If this track's SLS is less than the threshold, remove it
    if track.sls() < sls_threshold:
        return True

    # Otherwise, keep it
    return False
