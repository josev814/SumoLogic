#!/usr/bin/env python3
import sys
import logging
from logging import handlers
from .constants import SUMO_LOGFILE, DAEMON_LOG_TIME_FORMAT, DAEMON_LOG_MESSAGE_FORMAT


class LogMessage(object):

    def __init__(self, logger='SumoLogic'):
        self.logger = logger
        self.log_debug = logging.getLogger(self.logger).debug
        self.log_info = logging.getLogger(self.logger).info
        self.log_error = logging.getLogger(self.logger).error
        self.log_warning = logging.getLogger(self.logger).warning
        self.log_exception = logging.getLogger(self.logger).warning
        self.log_file = SUMO_LOGFILE

    def send_message(self, mtype=None, message=None, stop=False):
        if mtype == 'debug':
            self.log_debug(message)
        elif mtype == 'info':
            self.log_info(message)
        elif mtype == 'warning':
            self.log_warning(message)
        elif mtype == 'exception':
            self.log_exception(message)
        else:
            self.log_error(message)
        print('{}: {}'.format(mtype, message))
        if stop:
            self.teardown_logger()
            sys.exit(1)

    def get_level(self):
        return logging.getLogger(self.logger).getEffectiveLevel()

    def set_level(self, level):
        logging.getLogger().setLevel(level)

    def setup_logging(self, enable_debug):
        # define a Handler which writes INFO messages or higher to the sys.stderr
        try:
            fh = logging.handlers.RotatingFileHandler(self.log_file, 'a', maxBytes=1024 * 1024, backupCount=7)
            fh.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                DAEMON_LOG_MESSAGE_FORMAT,
                DAEMON_LOG_TIME_FORMAT
            )
            fh.setFormatter(formatter)
            # add the handler to the root logger
            logging.getLogger().addHandler(fh)
            if enable_debug:
                # if --debug was enabled provide gory activity details
                logging.getLogger().setLevel(logging.DEBUG)
                self.send_message('debug', 'SumoLogic Debugging Enabled')
            else:
                # in daemon mode we always log some activity
                logging.getLogger().setLevel(logging.INFO)

            self.send_message('info', 'SumoLogic Launched')
        except FileNotFoundError as e:
            print('Log File Error {} Error: {}'.format(self.log_file, e))
            exit(1)
        except IOError as e:
            print('Unable to access {} with IO ERROR: {}'.format(self.log_file, e))
            exit(1)

    def teardown_logger(self):
        logging.handlers.RotatingFileHandler(self.log_file).close()
        logging.shutdown()
