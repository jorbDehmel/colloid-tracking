'''
Tests the speckle.filters module and the speckle track filtering
methods contained therein.

Jordan Dehmel, 2024
'''

import unittest
from speckle import Track, BasicTrack, FreqFile
from speckle import filters as f


class TestFilters(unittest.TestCase):
    '''
    Tests the speckle.filters module, which provides various
    filters for speckle-based colloidal data.
    '''

    def setUp(self) -> None:
        '''
        Setup for each test case.
        '''

        # These should be setup identically
        self.normal = FreqFile()
        self.basic = FreqFile()

        a: Track = Track([0.0, 1.0, 2.0],
                         [0.0, 0.5, 1.0],
                         [1, 2, 3])

        b: Track = Track([0.0, -5.0, -10.0, -12.0],
                         [0.0, 1.0, 2.0, 1.0],
                         [1, 2, 3, 4])

        c: Track = Track([0.0, -20.0],
                         [0.0, -20.0],
                         [1, 2])

        for t in [a, b, c]:
            self.normal.tracks.append(t)
            self.basic.tracks.append(BasicTrack(t.duration(),
                                                t.displacement(),
                                                t.sls()))

    def tearDown(self) -> None:
        '''
        Teardown from each test case.
        '''

        del self.normal
        del self.basic

    def test_sls_threshold(self) -> None:
        '''
        Tests the sls threshold filter on the standard Track
        as well as the BasicTrack objects.
        '''

        self.assertEqual(self.basic.sls_mean(), self.normal.sls_mean())
        self.assertEqual(self.basic.sls_std(), self.normal.sls_std())

        self.basic.filter(f.sls_threshold_filter, sls_threshold=10.0)
        self.normal.filter(f.sls_threshold_filter, sls_threshold=10.0)

        self.assertEqual(self.basic.sls_mean(), self.normal.sls_mean())
        self.assertEqual(self.basic.sls_std(), self.normal.sls_std())
