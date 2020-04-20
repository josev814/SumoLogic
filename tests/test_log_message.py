import unittest
from SumoLogic.log_message import LogMessage
from os.path import dirname, join as ospj, isfile
from os import remove

class Test_Log_Message(unittest.TestCase):

    def setUp(self):
        self.log_message = LogMessage('SumoLogic')
        self.DIRECTORY = ospj(dirname(__file__), 'data', 'sumo_logic')
        self.WORK_DIR = ospj(self.DIRECTORY, 'work')
        self.log_message.log_file = ospj(self.WORK_DIR, 'sumolog')

    def test_01_setup_logging_with_debug(self):
        self.assertIsNone(self.log_message.setup_logging(True))

    def test_02_setup_logging_no_debug(self):
        self.assertIsNone(self.log_message.setup_logging(False))

    def test_03_send_messages(self):
        self.log_message.setup_logging(False)
        message_types = ['info', 'exception', 'error', 'debug', 'warning']
        for mtype in message_types:
            self.log_message.send_message(
                mtype,
                '{} log message'.format(mtype)
            )

    def test_04_get_logger_level(self):
        self.log_message.setup_logging(False)
        self.assertEqual(self.log_message.get_level(), 20)

    def test_05_set_logger_level(self):
        self.log_message.setup_logging(False)
        self.assertIsNone(self.log_message.set_level(30))
        self.assertEqual(self.log_message.get_level(), 30)

    def test_99_send_messages_and_close(self):
        self.log_message.setup_logging(False)
        with self.assertRaises(SystemExit):
            self.log_message.send_message(
                'info',
                'Closing Tests',
                True
            )
        self.assertIsNone(remove(self.log_message.log_file))
