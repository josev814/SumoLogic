import unittest
from os.path import dirname, join as ospj
from os import close

from SumoLogic.lockfile import LockFile


class LockFileTest(unittest.TestCase):
    def setUp(self):
        self.DIRECTORY = ospj(dirname(__file__), 'data', 'lockdir')
        self.LOCKPATH = ospj(self.DIRECTORY, 'lockfile')
        self.lockfile = LockFile(self.LOCKPATH)

    def test_01_check_lockfile_not_exists(self):
        self.assertFalse(self.lockfile.exists())

    def test_02_check_lockfile_create(self):
        self.assertIsNone(self.lockfile.create())
        close(self.lockfile.fd)

    def test_03_check_lockfile_exists(self):
        self.assertTrue(self.lockfile.exists())

    def test_04_check_pid(self):
        pid = self.lockfile.get_pid()
        self.assertRegex(pid, r'^[0-9]+$')

    def test_05_check_lockfile_create_exists(self):
        with self.assertRaises(SystemExit) as cm:
            self.lockfile.create()

    def test_06_check_lockfile_removal(self):
        self.assertIsNone(self.lockfile.remove())

    def test_07_check_lockfile_removal_not_exists(self):
        self.assertIsNone(self.lockfile.remove())

    def test_08_get_pid_empty(self):
        self.assertEqual(self.lockfile.get_pid(), '')

    def test_09_create_remove(self):
        self.assertIsNone(self.lockfile.create())
        self.assertIsNone(self.lockfile.remove())

