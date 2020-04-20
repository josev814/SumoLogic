from __future__ import print_function, unicode_literals

from os.path import dirname, join as ospj, isfile
import unittest
import sys
import time
from SumoLogic.prefs import SumoConfig
from SumoLogic.sync import Sync


class SyncTestStaticTimestamp(unittest.TestCase):
    """
    Tests that we can read the sync timestamp from the filesystem.
    """
    def setUp(self):
        self.DIRECTORY = dirname(__file__)
        self.WORK_DIR = ospj(self.DIRECTORY, 'data', 'sync')
        self.DYN_DIR = ospj(self.WORK_DIR, 'dynamic')
        self.STATIC_DIR = ospj(self.WORK_DIR, 'static')
        self.SUMO_DIR = ospj(self.DIRECTORY, 'data', 'sumo_logic')
        self.ETC_DIR = ospj(self.SUMO_DIR, 'etc')
        self.syslog_file = ospj(self.SUMO_DIR, 'var', 'log', 'syslog')
        self.default_config = ospj(self.ETC_DIR, 'config')
        self.user_config = ospj(self.ETC_DIR, 'user_overrides')
        self.sumoconfig = SumoConfig(self.default_config, self.user_config)
        self.sumoconfig.cp.set('default', 'work_dir', self.WORK_DIR)
        self.assertTrue(isfile(self.default_config))
        self.assertTrue(isfile(self.user_config))
        with open(ospj(self.STATIC_DIR, 'sync-timestamp'), 'r') as static_time_fh:
            self.static_time = int(static_time_fh.readline().strip())
        self.sync = Sync(self.sumoconfig, self.static_time)

    def test_request_response():
        url = 'http://localhost:{port}/users'.format(port=mock_server_port)

        # Send a request to the mock API server and store the response.
        response = requests.get(url)

        # Confirm that the request-response cycle completed successfully.
        assert_true(response.ok)

    def test_01_check_sync(self):
        self.assertTrue(self.sync.check_to_sync())

    def test_02_update_last_sync(self):
        self.assertIsNone(self.sync.update_last_sync_time())

    def test_03_check_sync_false(self):
        self.sync = Sync(self.sumoconfig, int(time.time()))
        self.assertFalse(self.sync.check_to_sync())

    def get_log_data(self):
        try:
            fh = open(self.syslog_file, 'r')
            self.log_lines.append(fh.readline())
            fh.close()
        except Exception as e:
            print(e)

    def test_04_send_new_logdata_missing_key(self):
        self.log_lines = []
        self.get_log_data()
        sumo_log_info = {'log_file': self.syslog_file}
        self.assertFalse(self.sync.send_new_logdata(self.log_lines, sumo_log_info))

    def test_05_send_new_logdata(self):
        self.log_lines = []
        self.get_log_data()
        sumo_log_info = {
            'log_file': self.syslog_file,
            'end_point': '127.0.0.1:8080'
        }
        self.assertFalse(self.sync.send_new_logdata(self.log_lines, sumo_log_info))

    #__send_new_data

    #__write_temp_data
