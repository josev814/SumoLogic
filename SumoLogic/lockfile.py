import os
from .log_message import LogMessage


class LockFile(object):
    def __init__(self, lockpath):
        self.lockpath = lockpath
        self.fd = None

    def exists(self):
        return os.access(self.lockpath, os.F_OK)

    def get_pid(self):
        pid = ""
        try:
            with open(self.lockpath, "r") as fp:
                pid = fp.read().strip()
        except IOError:
            pass
        return pid

    def create(self):
        try:
            if not os.path.isfile(self.lockpath):
                self.fd = os.open(self.lockpath,
                                  os.O_CREAT |  # create file
                                  os.O_TRUNC |  # truncate it, if it exists
                                  os.O_WRONLY |  # write-only
                                  os.O_EXCL,    # exclusive access
                                  0o644)         # file mode
            else:
                pid = self.get_pid()
                message = 'SumoLogic could not obtain lock (pid: {}), file.  Lock file, {} already exists'.format(
                    pid,
                    self.lockpath
                )
                LogMessage('lockfile').send_message('error', message, True)
        except Exception as e:
            pid = self.get_pid()
            message = 'SumoLogic could not obtain lock (pid: {}) Error: {}'.format(
                pid, e
            )
            LogMessage('lockfile').send_message('exception', message, True)

        s = '{}\n'.format(os.getpid())
        os.write(self.fd, s.encode('UTF-8'))
        os.fsync(self.fd)

    def remove(self, die_=True):
        try:
            if self.fd:
                os.close(self.fd)
        except IOError:
            pass

        self.fd = None
        try:
            if os.path.isfile(self.lockpath):
                os.unlink(self.lockpath)
        except Exception as e:
            if die_:
                message = 'Error deleting SumoLogic lock file for pid {}: {}'.format(
                    self.lockpath, e
                )
                LogMessage('lockfile').send_message('exception', message, True)
