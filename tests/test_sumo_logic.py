from __future__ import print_function, unicode_literals

from os.path import dirname, join as ospj
import unittest

from SumoLogic.sumo_logic import SumoLogic
from SumoLogic.lockfile import LockFile
from SumoLogic.prefs import Prefs

class SumoLogicBasicTest(unittest.TestCase):
    def setUp(self):
        self.directory = ospj(dirname(__file__), 'data/sumo_logic')
        self.work_dir = ospj(self.directory, 'work')
        self.logfile = ospj(self.work_dir, 'logfile')
        self.prefs = Prefs()

        self.lock_file = LockFile(ospj(self.directory, 'lockfile'))
        self.lock_file.remove(die_=False)
        self.lock_file.create()

        self.prefs._Prefs__data['ETC_DIR'] = ospj(self.directory, 'etc')
        self.prefs._Prefs__data['WORK_DIR'] = self.work_dir

    def test_init(self):
        SumoLogic(self.logfile, self.prefs, self.lock_file)

    def tearDown(self):
        self.lock_file.remove()
