'''
Tests the FreqFile class and other misc things in
speckle.freq_file.

Jordan Dehmel, 2024
'''

import unittest
from hypothesis import given, strategies as some
import os
from typing import Any, Union
import speckle as s
from speckle import speckle_filter


class TestFreqFile(unittest.TestCase):
    '''
    Test the FreqFile class. Many methods are already
    covered in other unit tests, so not all are included
    here.
    '''

    def setUp(self) -> None:
        '''
        Set up the test case.
        '''

        self.f = s.FreqFile()

        self.f.tracks.append(s.BasicTrack(5, 10.0, 4.0))
        self.f.tracks.append(s.BasicTrack(2, 100.0, 3.0))
        self.f.tracks.append(s.BasicTrack(10, 5.0, 2.0))
        self.f.tracks.append(s.BasicTrack(8, 2.0, 1.0))

    def test_save_tracks(self) -> None:
        '''
        Tests the `save_tracks` method of FreqFile.
        '''

        fp: str = 'test.tracks.csv'

        self.f.save_tracks(fp)
        self.assertTrue(os.path.exists(fp))
        os.remove(fp)

    def test_repr(self) -> None:
        '''
        Tests the FreqFile __repr__ method.
        '''

        _: str = repr(self.f)

    def test_erasure(self) -> None:
        '''
        Tests the methods surrounding track erasure for
        FreqFile.
        '''

        @speckle_filter
        def remove_all(track: Union[s.Track, s.BasicTrack],
                       **kwargs: Any) -> bool:

            _ = track, kwargs

            return True

        backup = self.f.tracks[:]

        self.f.filter(remove_all)

        self.assertEqual(len(self.f.tracks), 0)

        self.f.restore_erased()

        self.assertEqual(self.f.tracks, backup)

        self.f.filter(remove_all)

        removed = self.f.purge_erased()

        self.assertEqual(removed, backup)

        self.assertEqual(len(self.f.tracks), 0)


class TestBasicTrack(unittest.TestCase):
    '''
    Tests the BasicTrack class.
    '''

    def test_sls(self) -> None:
        '''
        Tests SLS (mean straight line speed) for the BasicTrack
        class. This is just a getter by definition.
        '''

        @given(some.floats(allow_nan=False))
        def test_on_value(value: float) -> None:
            self.assertEqual(s.BasicTrack(-1, -1, value).sls(), value)

        test_on_value()

    def test_displacement(self) -> None:
        '''
        Tests the displacement getter for the BasicTrack class.
        '''

        @given(some.floats(allow_nan=False))
        def test_on_value(value: float) -> None:
            self.assertEqual(s.BasicTrack(-1, value, -1.0).displacement(),
                             value)

        test_on_value()

    def test_duration(self) -> None:
        '''
        Tests the duration getter for the BasicTrack class.
        '''

        @given(some.integers())
        def test_on_value(value: int) -> None:
            self.assertEqual(s.BasicTrack(value, -1.0, -1.0).duration(),
                             value)

        test_on_value()


class TestFilter(unittest.TestCase):
    '''
    Tests FilterFunction typing.
    '''

    def test_filter_fn(self) -> None:
        '''
        Tests the type checking of a FilterFunction object. This
        is super finicky: It appears that you must have the
        same names for parameters, in addition to the same
        types.
        '''

        @speckle_filter
        def filter_fn(track: Union[s.Track, s.BasicTrack],
                      **kwargs: Any) -> bool:
            '''
            A dummy filter function to ensure that the type
            checking works. More specifically, this removes all
            BasicTracks while leaving all Tracks.
            '''

            _ = kwargs

            return isinstance(track, s.BasicTrack)

        filterer: s.FilterFunction = filter_fn

        self.assertFalse(s.FilterFunction.__call__(filterer,
                                                   s.Track([], [], [])))
        self.assertFalse(filterer(s.Track([], [], [])))
