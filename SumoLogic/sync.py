# Built-ins
from time import time  # 0.0 MB
from sys import exc_info  # 0.0 MB
from gzip import GzipFile  # 0.2734375
from io import BytesIO, TextIOWrapper  # 0.0
from socket import gethostname  # 0.0

# Third Party
#import requests
from requests import Session, adapters  # 3.58203125
#import urllib3
from urllib3.util.retry import Retry  #0.0

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
        if int(time()) - self.last_sync >= sync_interval:
            return True
        return False

    def update_last_sync_time(self):
        self.last_sync = int(time())

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
            # print(exc_info())
            return False
        return True

    def __send_new_data(self, lines, endpoint):
        try:
            zipped_data = self.__zipped_temp_data(lines)
            session = Session()
            retry = Retry(backoff_factor=10, total=5, status_forcelist=[429, 500, 502, 503, 504])
            adapter = adapters.HTTPAdapter(max_retries=retry)
            for protocol in ['http', 'https']:
                session.mount('{}://'.format(protocol), adapter)
            r = session.post(
                url=endpoint,
                data=zipped_data,
                headers={'Content-Encoding': 'gzip', 'X-Sumo-Host': gethostname()}

            )
            if r.status_code != 200:
                self.log_message.send_message('error', 'Status Code: {}'.format(r.status_code))
                self.log_message.send_message('error', 'Failure Reply From Sumo: {}'.format(r.content), True)

            del zipped_data
            del r
            self.log_message.send_message('debug', 'Sent gzip data to SumoLogic')
        except Exception as e:
            self.log_message.send_message(
                'exception',
                '__send_new_data Error: {}'.format(e),
                True
            )

    def __zipped_temp_data(self, lines):
        try:
            fgz = BytesIO()
            with GzipFile(mode='wb', compresslevel=9, fileobj=fgz) as gh:
                with TextIOWrapper(gh, encoding='utf-8') as enc:
                    for line in lines:
                        enc.write(line)
        except Exception as e:
            self.log_message.send_message(
                'exception',
                '__zipped_temp_data Error: {}'.format(e),
                True
            )
            print(exc_info())
        return fgz.getvalue()
