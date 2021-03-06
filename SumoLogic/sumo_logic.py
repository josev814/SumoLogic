#!/usr/bin/env python3
# Built-in Libraries
from os.path import join as ospj
import os
import sys
import signal
import time
from logging import INFO as LOG_INFO, DEBUG as LOG_DEBUG
import socket
from stat import ST_SIZE, ST_INO

# Third Party Libraries
import gzip
try:
    import bz2
    HAS_BZ2 = True
except ImportError:
    HAS_BZ2 = False
    bz2 = None

# Package Libraries
from .constants import *
from .log_message import LogMessage
from .prefs import SumoConfig
from .version import VERSION
from .daemon import createdaemon
from .file_tracker import FileTracker
from .sync import Sync
from .util import calculate_seconds

HOSTNAME = socket.gethostname()


class SumoLogic(object):

    def __init__(self, config, user_config, logfile, prefs, lock_file, ignore_offset=0, first_time=0, daemon=0, foreground=0):
        self.__prefs = prefs
        self.__lock_file = lock_file
        self.__first_time = first_time
        self.__daemon = daemon
        self.__foreground = foreground
        self.__logfile = logfile
        self.sync_lines = []
        # set last sync to current time
        self.sync = Sync(self.__prefs, time.time())

        self.sumoconfig = SumoConfig(config, user_config)
        self.log_message = LogMessage('SumoLogic')
        self.__sync_interval = calculate_seconds(self.sumoconfig.get_value('default', 'sync_interval'))
        self.__daemon_sleep = calculate_seconds(self.sumoconfig.get_value('default', 'daemon_sleep'))

        try:
            self.file_tracker = FileTracker(
                ospj(self.sumoconfig.get_value('default', 'work_dir'), OFFSETS_DIR),
                logfile
            )
        except Exception as e:
            self.__lock_file.remove()
            self.log_message.send_message(
                'error',
                'Can\'t read file {} with error: {}'.format(
                    logfile['log_file'],
                    e
                ),
                True
            )
        if ignore_offset:
            last_offset = 0
        else:
            last_offset = self.file_tracker.get_offset()

        if last_offset is not None:
            self.log_message.send_message(
                'info',
                'Processing log file {} from offset {}'.format(
                    logfile['log_file'],
                    last_offset
                )
            )
            offset = self.process_log(logfile, last_offset)
            if offset != last_offset:
                self.file_tracker.save_offset(offset)
                last_offset = offset
        elif foreground:
            print(
                'Log file,{}, size has not changed.  Nothing to do.'.format(
                    logfile['log_file']
                )
            )

        if daemon and not foreground:
            self.log_message.send_message(
                'info',
                'Launching SumoLogic Daemon (version {}, for log file {})'.format(
                    VERSION,
                    logfile['log_file']
                )
            )

            # remove lock file since createDaemon will
            # create a new pid.  A new lock
            # will be created when runDaemon is invoked
            createdaemon(self.rundaemon, {'logfile': logfile, 'last_offset': last_offset})
        elif foreground:
            print('Launching SumoLogic (Version {})....'.format(VERSION))
            self.__lock_file.remove()
            self.rundaemon(logfile, last_offset)

    def killdaemon(self, arg1, arg2):
        self.log_message.send_message(
            'debug',
            'Received Args {}, {}'.format(arg1, arg2)
        )
        self.log_message.send_message(
            'debug',
            'Received SIGTERM for {}'.format(os.getpid())
        )
        self.log_message.send_message(
            'info',
            'SumoLogic daemon is shutting down child: {}'.format(self.__logfile['log_file'])
        )
        # signal handler

        self.__lock_file.remove()
        # lock will be freed on SIGTERM by sumologic.py
        # exception handler (SystemExit)
        sys.exit(0)

    def toggledebug(self):
        level = self.log_message.get_level()
        if level == LOG_INFO:
            level = LOG_DEBUG
            name = "DEBUG"
        else:
            level = LOG_INFO
            name = "INFO"
        self.log_message.send_message(
            'info',
            'Setting Debug Level to {}'.format(name)
        )
        self.log_message.set_level(level)

    def rundaemon(self, logfile, last_offset):
        # signal.signal(signal.SIGHUP, self.killdaemon)
        signal.signal(signal.SIGTERM, self.killdaemon)
        signal.signal(signal.SIGUSR1, self.toggledebug)

        self.log_message.send_message(
            'info',
            'SumoLogic daemon is now running, pid: {}'.format(os.getpid())
        )
        self.log_message.send_message(
            'info',
            'send daemon process a TERM signal to terminate cleanly'
        )
        self.log_message.send_message(
            'info',
            '  eg.  kill -TERM {}'.format(os.getpid())
        )
        self.__lock_file.create()

        self.log_message.send_message(
            'info',
            'monitoring log: {}'.format(logfile['log_file'])
        )
        self.daemonloop(logfile, last_offset)

    def daemonloop(self, logfile, last_offset):
        fp = open(logfile['log_file'], "r")
        inode = os.fstat(fp.fileno())[ST_INO]

        while True:
            try:
                curr_inode = os.stat(logfile['log_file'])[ST_INO]
            except OSError:
                self.log_message.send_message(
                    'exception',
                    '{} has been deleted'.format(logfile['log_file'])
                )
                time.sleep(self.__daemon_sleep)
                continue

            try:
                if curr_inode != inode:
                    self.log_message.send_message(
                        'info',
                        '%s has been rotated'.format(logfile['log_file'])
                    )
                    inode = curr_inode
                    try:
                        fp.close()
                    except IOError:
                        pass

                    fp = open(logfile['log_file'], "r")
                    # this ultimately forces offset (if not 0) to be < last_offset
                    last_offset = sys.maxsize

                offset = os.fstat(fp.fileno())[ST_SIZE]
                if last_offset is None:
                    last_offset = offset

                if offset > last_offset:
                    # new data added to logfile
                    self.log_message.send_message(
                        'debug',
                        '{} has additional data'.format(logfile['log_file'])
                    )
                    last_offset = self.process_log(logfile, last_offset)

                    self.file_tracker.save_offset(last_offset)
                elif offset == 0:
                    # log file rotated, nothing to do yet...
                    # since there is no first_line
                    self.log_message.send_message(
                        'debug',
                        '{} is empty. File was rotated'.format(logfile['log_file'])
                    )
                elif offset < last_offset:
                    # file was rotated or replaced and now has data
                    self.log_message.send_message(
                        'debug',
                        '{} most likely rotated and now has data'.format(logfile['log_file'])
                    )
                    last_offset = 0
                    self.file_tracker.update_first_line()
                    continue
                time.sleep(self.__daemon_sleep)
            except KeyboardInterrupt:
                self.__lock_file.remove()
                msg = "SumoLogic exited by user with Keyboard interrupt"
                self.log_message.send_message('exception', msg, True)
                print("\n{}".format(msg))

    def process_log(self, logfile_info, offset):
        try:
            if logfile_info['log_file'].endswith(".gz"):
                fp = gzip.open(logfile_info['log_file'], 'r')
            elif logfile_info['log_file'].endswith(".bz2"):
                if HAS_BZ2:
                    fp = bz2.BZ2File(logfile_info['log_file'], 'r')
                else:
                    raise Exception("Can not open bzip2 file (missing bz2 module)")
            else:
                fp = open(logfile_info['log_file'], 'r')
        except Exception as e:
            self.log_message.send_message(
                'error',
                'Could not open log file, {}, with error {}'.format(
                    logfile_info['log_file'],
                    e
                )
            )
            return -1

        try:
            fp.seek(offset)
        except IOError:
            pass

        line = fp.readline()
        while line:
            self.sync_lines.append(line)
            line = fp.readline()

        offset = fp.tell()
        fp.close()

        if self.sync.check_to_sync(self.__sync_interval):
            if self.sync.send_new_logdata(self.sync_lines, logfile_info):
                self.sync_lines = []

        return offset

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.log_message.send_message('info', 'Exiting Child Process for {}'.format(self.log_file['file_path']))
        self.__lock_file.remove()
