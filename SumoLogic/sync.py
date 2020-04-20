# Built-ins
import time
from os import unlink
from os.path import join as ospj
import sys
import gzip
from io import BytesIO, TextIOWrapper
import socket

# Third Party
import requests
from uuid import uuid4

# Package Libraries
from .log_message import LogMessage


class Sync(object):
    def __init__(self, sumoconfig, last_sync):
        self.log_message = LogMessage('sync')
        self.__sumoconfig = sumoconfig
        self.__work_dir = sumoconfig.get_value('default', 'work_dir')
        self.__connected = False
        self.__server = None
        self.last_sync = last_sync

    def check_to_sync(self, sync_interval):
        if int(time.time()) - self.last_sync >= sync_interval:
            return True
        return False

    def update_last_sync_time(self):
        self.last_sync = int(time.time())

    def send_new_logdata(self, new_log_lines, sumo_info):
        self.log_message.send_message(
            'debug',
            'send_new log file lines from {}'.format(sumo_info['log_file'])
        )

        try:
            self.__send_new_data(new_log_lines, sumo_info['endpoint'])
            self.log_message.send_message(
                'info',
                'Sent {} new log lines for log file {}'.format(
                    len(new_log_lines),
                    sumo_info['log_file']
                )
            )
            self.update_last_sync_time()
        except KeyError as ke:
            self.log_message.send_message('exception', 'Missing dict key: {}'.format(ke))
            return False
        except Exception as e:
            self.log_message.send_message('exception', e)
            # print(sys.exc_info())
            return False
        return True

    def __send_new_data(self, lines, endpoint):
        try:
            zipped_file, zipped_data = self.__zipped_temp_data(lines)
            r = requests.post(
                url=endpoint,
                data=zipped_data,
                headers={'Content-Encoding': 'gzip', 'X-Sumo-Host': socket.gethostname()}
            )
            if r.status_code != 200:
                self.log_message.send_message('error', 'Status Code: {}'.format(r.status_code))
                self.log_message.send_message('error', 'Failure Reply From Sumo: {}'.format(r.content), True)

            del zipped_data
            del zipped_file
            self.log_message.send_message('debug', 'Sent gzip data to SumoLogic')
        except Exception as e:
            self.log_message.send_message(
                'exception',
                '__send_new_data Error: {}'.format(e),
                True
            )

    def __zipped_temp_data(self, lines):
        try:
            uid = uuid4()
            uid_file = ospj(self.__work_dir, '{}.gz'.format(uid))
            fgz = BytesIO()
            with gzip.GzipFile(filename=uid_file, mode='wb', compresslevel=9, fileobj=fgz) as gh:
                with TextIOWrapper(gh, encoding='utf-8') as enc:
                    enc.writelines(lines)
        except Exception as e:
            self.log_message.send_message(
                'exception',
                '__zipped_temp_data Error: {}'.format(e),
                True
            )
            print(sys.exc_info())
        return uid_file, fgz.getvalue()
