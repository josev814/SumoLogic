from os.path import join as ospj
from .log_message import LogMessage


class FileTracker(object):
    """
    Tracks a Log File to get the current location of the file to pick up from
    Keeps track of the first line of the file to know if the file has been rotated
    Init gets the current offset in the logfile file
    use get_offset to check the last offset we read to
    """

    def __init__(self, work_dir, logfile):
        """
        Sets up the File Tracker with the directory and log file to track
            Also gets the current first_line and offset that were last processed
        :param work_dir: the directory the offset file information is saved in
        :param logfile: dict of log_file information must include log_file being tracked and offset_file to use
        """
        self.log_message = LogMessage('filetracker')
        self.work_dir = work_dir
        self.logfile = logfile['log_file']
        self.offset_file = logfile['offset_file']
        (self.__first_line, self.__offset) = self.__get_current_offset()

    def __get_last_offset(self):
        offset_file = ospj(self.work_dir, self.offset_file)
        first_line_of_file = ""
        offset = 0
        try:
            fh = open(offset_file, 'r')
            first_line_of_file = self.__get_first_line(fh)
            offset_line = fh.readline()
            if offset_line is None or offset_line == '':
                offset = 0
            else:
                offset = int(offset_line)
            fh.close()
        except IOError:
            pass

        self.log_message.send_message(
            'debug',
            '__get_last_offset():  first_line: {}  offset {}'.format(
                first_line_of_file,
                offset
            )
        )

        return first_line_of_file, offset

    @staticmethod
    def __get_first_line(fh):
        fh.seek(0, 0)
        line = fh.readline()
        if line.endswith('\n'):
            line = line[:-1]
        return line

    @staticmethod
    def __get_end_of_file_position(fh):
        fh.seek(0, 2)
        return fh.tell()

    def __get_current_offset(self):
        """
        Gets the current first line and offset of the log file
        :return: str(first_line), int(offset)
        """
        try:
            fh = open(self.logfile, 'r')
            first_line = self.__get_first_line(fh)
            offset = self.__get_end_of_file_position(fh)
            fh.close()
        except FileNotFoundError:
            offset = 0
            first_line = ''
            pass
        except IOError as e:
            self.log_message.send_message(
                'error',
                '{}'.format(e),
                True
            )

        self.log_message.send_message(
            'debug',
            '__get_current_offset():  first_line: {}  offset {}'.format(
                first_line,
                offset
            )
        )

        return first_line, offset

    def update_first_line(self):
        try:
            fp = open(self.logfile, "r")
            first_line = fp.readline()[:-1]
            fp.close()
        except IOError as e:
            self.log_message.send_message(
                'error',
                '{}'.format(e),
                True
            )

        self.__first_line = first_line

    def get_offset(self):
        """
        Gets the last offset we read to
        Then determines if the log file was changed or if we should read new lines from the log file
        :return: int(offset) returns the current offset we read to
        """
        last_line, last_offset = self.__get_last_offset()

        if last_line != self.__first_line:
            # log file was rotated, start from beginning
            offset = 0
        elif self.__offset > last_offset:
            # new lines exist in log file
            offset = last_offset
        else:
            # no new entries in log file default
            offset = None

        self.log_message.send_message(
            'debug',
            'get_offset():  offset: {}'.format(offset)
        )

        return offset

    def save_offset(self, offset):
        path = ospj(self.work_dir, self.offset_file)
        try:
            with open(path, "w") as fp:
                fp.writelines([
                    "{}\n".format(self.__first_line),
                    "{}\n".format(offset)
                ])
        except IOError:
            self.log_message.send_message(
                'error',
                'Could not save logfile offset to {}'.format(
                    path
                ),
                True
            )
