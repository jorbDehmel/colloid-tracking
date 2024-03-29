'''
Tests speckle.Track
'''

import os
import shutil
import unittest
from typing import List
import speckle as s


class TestTrack(unittest.TestCase):
    '''
    Tests the Track class from speckle.
    '''

    def test_append(self) -> None:
        '''
        Tests Track.append
        '''

        t: s.Track = s.Track([0.0], [0.0], [0])

        t.append(3.0, 4.0, 1)

        self.assertAlmostEqual(t.displacement(), 5.0, 5)

    def test_sls(self) -> None:
        '''
        Tests Track.sls
        SLS = mean Straight Line Speed
            = (displacement) / (duration)
        This is the thing we have been measuring, so this test
        is most important.
        '''

        t: s.Track = s.Track([0.0], [0.0], [0])

        self.assertEqual(t.sls(), 0.0)

        t.append(-3.0, -4.0, 1)
        t.append(3.0, 4.0, 2)

        self.assertAlmostEqual(t.sls(), 2.5, 5)

    def test_mdts(self) -> None:
        '''
        Tests Track.mdts
        MDTS = Mean Distance Travelled Speed
             = (total distance travelled) / (duration)
        '''

        t: s.Track = s.Track([0.0], [0.0], [0])

        self.assertEqual(t.mdts(), 0.0)

        t.append(-3.0, -4.0, 1)
        t.append(3.0, 4.0, 2)

        self.assertAlmostEqual(t.mdts(), 7.5, 5)

    def test_mv(self) -> None:
        '''
        Tests Track.mv
        MV = Mean Velocity
           = sum(velocities) / len(velocities)
        '''

        t: s.Track = s.Track([0.0], [0.0], [0])

        self.assertEqual(t.mv(), 0.0)

        t.append(-3.0, -4.0, 1)
        t.append(3.0, 4.0, 2)

        self.assertAlmostEqual(t.mv(), 7.5, 5)

    def test_duration(self) -> None:
        '''
        Tests Track.duration
        '''

        t: s.Track = s.Track([0.0], [0.0], [0])

        t.append(-3.0, -4.0, 1)
        t.append(3.0, 4.0, 2)

        self.assertEqual(t.duration(), 3)

    def test_displacement(self) -> None:
        '''
        Tests Track.displacement
        '''

        t: s.Track = s.Track([0.0], [0.0], [0])

        t.append(-3.0, -4.0, 1)
        t.append(3.0, 4.0, 2)

        self.assertAlmostEqual(t.displacement(), 5.0, 5)

    def test_msd(self) -> None:
        '''
        Tests Track.msd
        MSD = Mean Squared Displacement
            = sum((cur - origin)^2) / len(points)
        '''

        t: s.Track = s.Track([0.0], [0.0], [0])

        t.append(-3.0, -4.0, 1)
        t.append(3.0, 4.0, 2)

        self.assertAlmostEqual(t.msd(), 25.0, 5)

        self.assertEqual(s.Track([0.0], [0.0], [0]).msd(), 0.0)


class TestMiscSpeckleFunctions(unittest.TestCase):
    '''
    Tests misc functions from speckle.speckle which are not
    otherwise covered (IE for_each_file, for_each_dir, etc).
    '''

    def setUp(self) -> None:
        '''
        Set up the file structure needed in order to properly
        test the file operations.
        '''

        # Basic variable setup
        self.avi_path: str = 'test.avi.testcase'
        self.speckles_path: str = 'test.speckles.csv.testcase'
        self.tracks_path: str = 'test.tracks.csv.testcase'

        self.__root: str = 'TESTING'

        # Ensure that the testing files exists
        self.assertTrue(os.path.exists('tests/' + self.avi_path))
        self.assertTrue(os.path.exists('tests/' + self.speckles_path))
        self.assertTrue(os.path.exists('tests/' + self.tracks_path))

        # Create testing dir
        if not os.path.isdir(self.__root):
            os.mkdir(self.__root)

        # Member variables which are useful later
        self.folders: List[str] = ['A', 'B', 'C', 'C/D']
        self.files: List[str] = ['a.txt', 'b.txt', 'C/c.txt']

        # Copy testing files to testing dir
        shutil.copy('tests/' + self.avi_path,
                    self.__root + '/' + self.avi_path + '.avi')
        shutil.copy('tests/' + self.speckles_path,
                    self.__root + '/' + self.speckles_path)
        shutil.copy('tests/' + self.tracks_path,
                    self.__root + '/' + self.tracks_path)

        self.avi_path += '.avi'

        # Move to testing dir
        self.__og_dir: str = os.getcwd()
        os.chdir(self.__root)

        # Create folders
        for folder in self.folders:
            os.mkdir(folder)

        # Write files
        for file in self.files:
            with open(file, 'wb') as f:
                f.write(b'foobar')

    def tearDown(self) -> None:
        '''
        Erase the testing file structure put in place by
        `setUpClass`.
        '''

        os.chdir(self.__og_dir)
        shutil.rmtree(self.__root)

    def test_for_each_file(self) -> None:
        '''
        Tests speckle.for_each_file
        '''

        visited: List[str] = []

        def log_file(filepath: str) -> None:
            nonlocal visited
            visited.append(filepath)

        s.for_each_file(log_file)

    def test_for_each_dir(self) -> None:
        '''
        Tests speckle.for_each_dir
        '''

        visited: List[str] = []

        def log_dir(dir_path: str) -> None:
            nonlocal visited
            visited.append(dir_path)

        s.for_each_dir(log_dir)

    def test_reformat_avi(self) -> None:
        '''
        Tests speckle.reformat_avi
        '''

        s.reformat_avi(self.avi_path, 'foobar.avi')
        self.assertTrue(os.path.exists('foobar.avi'))

    def test_process_file(self) -> None:
        '''
        Tests speckle.process_file
        '''

        s.process_file(self.speckles_path, 'spots.csv', 'tracks.csv')

    def test_load_frequency_file(self) -> None:
        '''
        Tests load_frequency_file from freq_file.py.
        '''

        s.load_frequency_file(self.tracks_path)

        with self.assertRaises(NotImplementedError):
            s.load_frequency_file(self.speckles_path, 'speckles')
