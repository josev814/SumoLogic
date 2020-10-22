#!/usr/bin/env python3
import os
from platform import node
import sys
from uuid import uuid4
from multiprocessing import Process
from SumoLogic.constants import *
sys.path.insert(0, SUMOLOGIC_SHARE)

from getopt import getopt, GetoptError
import traceback

from SumoLogic.log_message import LogMessage
from SumoLogic.lockfile import LockFile

from SumoLogic.prefs import SumoConfig
from SumoLogic.version import VERSION
from SumoLogic.sumo_logic import SumoLogic
from SumoLogic.constants import *
from SumoLogic.util import is_true
#################################################################################

logger = LogMessage('SumoLogic')


def usage():
    print("Usage:")
    print('{0} [ -c configfile | --config configfile] [ -u configfile | --user_config configfile] '
          '[-i | --ignore] [-l | --unlock] '
          '[--daemon] [--version]'.format(sys.argv[0]))
    print("\n\n")
    print(" --config: The pathname of the configuration file")
    print(" --user_config: The pathname of the user configuration file for overriding defaults")
    print(" --ignore: Ignore last processed offset (start processing from beginning)")
    print(" --unlock: if lockfile exists, remove it and run as normal")
    print(" --daemon: run SumoLogic in daemon mode")
    print(" --foreground: run SumoLogic in foreground mode")
    print(" --version: Prints the version of SumoLogic and exits")


#################################################################################
#################################################################################

def create_default_dirs(dirs=[]):
    for adir in dirs:
        if os.path.isdir(adir) is False:
            os.mkdir(adir)
            logger.send_message('debug', 'Creating Dir: {}'.format(adir))

if __name__ == '__main__':
    config_file = os.path.join(CONFIG_DIR, CONFIG_FILE)
    user_config_file = os.path.join(USER_CONFIG_DIR, CONFIG_FILE)
    create_default_dirs([CONFIG_DIR, USER_CONFIG_DIR, SUMOLOGIC_SHARE])
    ignore_offset = False
    daemon = False
    foreground = False
    unlock = False
    args = sys.argv[1:]
    try:
        (opts, getopts) = getopt(
            args,
            'c:u:fdil?hVv',
            ["ignore", "help", "config=", "user_config=", "version", "daemon", "foreground", "unlock"]
        )
    except GetoptError:
        print("\nInvalid command line option detected.")
        usage()
        exit(1)

    for opt, arg in opts:
        if opt in ('-v', '-V', '--version'):
            print('SumoLogic version: {}'.format(VERSION))
            exit(0)
        if opt in ('-h', '-?', '--help'):
            usage()
            exit(0)
        if opt in ('-i', '--ignore'):
            ignore_offset = True
        if opt in ('-c', '--config'):
            config_file = arg
        if opt in ('-u', '--user_config'):
            user_config_file = arg
        if opt in ('-l', '--unlock'):
            unlock = True
        if opt in ('-d', '--daemon'):
            daemon = True
        if opt in ('-f', '--foreground'):
            foreground = True


    # This is generally expected to be in the environment, but there's no
    # non-hackish way to get systemd to set it, so just hack it in here.
    os.environ['HOSTNAME'] = node()

    prefs = SumoConfig(config_file, user_config_file)

    first_time = 0
    try:
        work_dir = prefs.get_value('default', 'work_dir')
        offset_dir = os.path.join(work_dir, OFFSETS_DIR)
        if not os.path.exists(work_dir) or not os.path.exists(offset_dir) or not os.path.exists(PID_DIRECTORY):
            create_default_dirs([work_dir, offset_dir, PID_DIRECTORY])
            first_time = 1
    except Exception as e:
        if e[0] != 17:
            print(e)
            exit(1)

    debug_mode = False
    if is_true(prefs.get_value('default', 'debug')):
        debug_mode = True

    logger.setup_logging(debug_mode)

    log_files = prefs.get_active_log_files()
    lock_file = LockFile(PID_FILE)

    if unlock:
        if os.path.isfile(PID_FILE):
            lock_file.remove()

    lock_file.create()

    try:
        for f in log_files:
            if not os.path.isfile(f['log_file']):
                logger.send_message('error', 'Log file, {}, doesn\'t exist. Skipping opening child'.format(f['log_file']))
                continue
            child = uuid4()
            logger.send_message('debug', 'Starting new child for {} as child {}'.format(f['log_file'], child))
            logger.send_message('debug', "Child: {} - {}".format(child, f['log_file']))
            CHILD_PID_FILE = os.path.join(PID_DIRECTORY, 'child-{}.pid'.format(child))
            child_lock_file = LockFile(CHILD_PID_FILE)
            if unlock:
                if os.path.isfile(CHILD_PID_FILE):
                    child_lock_file.remove()
            if daemon:
                SumoLogic(
                    config_file,
                    user_config_file,
                    f,
                    prefs,
                    child_lock_file,
                    ignore_offset,
                    first_time,
                    daemon,
                    foreground)
            else: #foreground
                dh = Process(
                    target=SumoLogic,
                    kwargs={
                        'config': config_file,
                        'user_config': user_config_file,
                        'logfile': f,
                        'prefs': prefs,
                        'lock_file': child_lock_file,
                        'ignore_offset': ignore_offset,
                        'first_time': first_time,
                        'daemon': daemon,
                        'foreground': foreground
                    },
                    daemon=False
                )
                dh.start()
    except KeyboardInterrupt:
        lock_file.remove()
        msg = "SumoLogic exited by user"
        logger.send_message('exception', msg, True)
        print("\n{}".format(msg))
        pass
    except SystemExit as e:
        lock_file.remove()
        msg = "SumoLogic SystemExit"
        logger.send_message('exception', msg, True)
        print("\n{}".format(msg))
        pass
    except Exception as e:
        lock_file.remove()
        traceback.print_exc(file=sys.stdout)
        msg = "SumoLogic exited abnormally"
        logger.send_message('exception', msg, True)
        print("\n{}".format(msg))

    # remove lock file on exit
    lock_file.remove()
    logger.send_message('info', 'SumoLogic exited')
    if len(log_files) == 0:
        msg = 'No Active Endpoints Found. Please configure your SumoLogic Endpoints.'
        logger.send_message('info', msg)
        print("\n{}".format(msg))
