#!/usr/bin/env python3
import os


#################################################################################
#        System Level Information Needed                                        #
#################################################################################
PID_DIRECTORY = r'/var/run/sumologic'
PID_FILE = os.path.join(PID_DIRECTORY, 'sumologic.pid')
SUMO_LOGFILE = r'/var/log/sumologic'
CONFIG_DIR = r'/etc/sumologic'
CONFIG_FILE = 'config'
USER_CONFIG_DIR = os.path.join(CONFIG_DIR, 'config.d')
SUMOLOGIC_SHARE = '/usr/share/sumologic'

#################################################################################
#        These directories will be created relative to config WORK_DIR          #
#################################################################################

OFFSETS_DIR = "offsets"

#################################################################################
#                           Miscellaneous constants                             #
#################################################################################

SUMO_DELIMITER = "# SumoLogic:"
ENTRY_DELIMITER = " | "

TIME_SPEC_LOOKUP = {
    's': 1,         # s
    'm': 60,        # minute
    'h': 3600,      # hour
    'd': 86400,     # day
    'w': 604800,    # week
    'y': 31536000,  # year
}

SYSLOG_REPORT = False
DAEMON_LOG_TIME_FORMAT = None
DAEMON_LOG_MESSAGE_FORMAT = '%(asctime)s - %(name)-12s: %(levelname)-8s %(message)s'