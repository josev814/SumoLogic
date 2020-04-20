from __future__ import print_function, unicode_literals

import unittest

from os.path import dirname, join as ospj
import SumoLogic.util as util
from datetime import datetime


class UtilsTest(unittest.TestCase):

    def setUp(self):
        self.true_strings = ['1', 't', 'true', 'y', 'yes']
        self.false_strings = ['', 'false', 'ye', 'tr', '0']
        self.work_dir = ospj(dirname(__file__), 'data/utils/')
        self.log_file = ospj(self.work_dir, 'daemon.log')

    def test_is_true(self):
        for string in self.true_strings:
            self.assertTrue(util.is_true(string))

    def test_fail_is_true(self):
        for string in self.false_strings:
            self.assertTrue(util.is_false(string))

    def test_is_false(self):
        for string in self.true_strings:
            self.assertFalse(util.is_false(string))

    def test_fail_time_spec(self):
        with self.assertRaises(TypeError) as te:
            util.get_time_spec(12345)

        with self.assertRaises(Exception) as ge:
            util.get_time_spec('s123 &$^')

    def test_seconds(self):
        self.assertEqual(util.calculate_seconds(1), 1)

    def test_invalid_seconds_format(self):
        with self.assertRaises(Exception) as cm:
            util.calculate_seconds('{} swv&$*#'.format(datetime.now()))
            self.assertEqual(cm.exception, 'Error')

    def test_seconds_zero_false(self):
        with self.assertRaises(Exception) as cm:
            util.calculate_seconds('0', False)

    def test_seconds_zero_true(self):
        self.assertEqual(util.calculate_seconds('0m', True), 0)

    def test_whitespace(self):
        self.assertEqual(
            util.normalize_whitespace('testing whitespace  for   sumologic'),
            'testing whitespace for sumologic'
        )
