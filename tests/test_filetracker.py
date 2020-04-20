import unittest
from os.path import dirname, join as ospj

from SumoLogic.file_tracker import FileTracker

class FileTrackerTest(unittest.TestCase):
    def setUp(self):
        self.DIRECTORY = ospj(dirname(__file__), 'data', 'filetracker')
        self.WORK_DIR = ospj(self.DIRECTORY, 'work')
        self.LOG_FILE = ospj(self.WORK_DIR, 'logfile')
        self.OFFSET_FILE = ospj(self.WORK_DIR, 'offset')
        self.LOG_FILE_DICT = {'log_file': self.LOG_FILE, 'offset_file': self.OFFSET_FILE}
        self.file_tracker = FileTracker(self.WORK_DIR, self.LOG_FILE_DICT)

    def write_entry(self, entry):
        with open(self.LOG_FILE, 'a') as fh:
            fh.write(entry)

    def test_01_check_offset_no_file(self):
        self.assertEqual(self.file_tracker.get_offset(), None)

    def test_02_create_log_file_with_entry(self):
        line = '[03/Apr/2020:11:45:31 -0400] 107.77.226.99 TLSv1.2 ECDHE-RSA-AES128-GCM-SHA256 "GET /js/76.0b813f2b6b182c88c9ad.chunk.js HTTP/1.1" 3139'
        self.write_entry(line)

    def test_03_check_offset(self):
        self.assertEqual(self.file_tracker.get_offset(), 0)

    def test_04_update_offset(self):
        """136 is how many characters are in the line create for test 2"""
        self.assertIsNone(self.file_tracker.save_offset(136))

    def test_05_update_first_line(self):
        self.assertIsNone(self.file_tracker.update_first_line())

    def test_06_validate_offset_after_multiple_new_entries(self):
        lines = [
            {
                'line': '\n[03/Apr/2020:11:45:31 -0400] 107.77.226.99 TLSv1.2 ECDHE-RSA-AES128-GCM-SHA256 "GET /js/2.0b813f2b6b182c88c9ad.chunk.js HTTP/1.1" 681978',
                'offset': 136,
                'new_offset': 273,
            },
            {
                'line': '\n[03/Apr/2020:11:45:32 -0400] 107.77.226.99 TLSv1.2 ECDHE-RSA-AES128-GCM-SHA256 "GET /js/2.0b813f2b6b182c88c9ad.chunk.js HTTP/1.1" 681979',
                'offset': 273,
                'new_offset': 409
            }
        ]
        for line_dict in lines:
            self.write_entry(line_dict.get('line'))
            ft = FileTracker(self.WORK_DIR, self.LOG_FILE_DICT)
            self.assertEqual(ft.get_offset(), line_dict.get('offset'))
            ft.save_offset(line_dict.get('new_offset'))

    def clear_offset_file(self):
        with open(ospj(self.WORK_DIR, self.LOG_FILE_DICT['offset_file']), 'w') as fh:
            fh.write('')

    def test_07_bug_99(self):
        self.clear_offset_file()
        ft = FileTracker(self.WORK_DIR, self.LOG_FILE_DICT)
        self.assertEqual(ft.get_offset(), 0)

    def test_08_cleanup(self):
        from os import unlink
        unlink(ospj(self.WORK_DIR, self.LOG_FILE_DICT['log_file']))
        unlink(ospj(self.WORK_DIR, self.LOG_FILE_DICT['offset_file']))