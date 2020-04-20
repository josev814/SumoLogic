import configparser
import traceback
import os
from .log_message import LogMessage


class SumoConfig(object):
    active_endpoints = []

    def __init__(self, config, user_config):
        self.logger = LogMessage('SumoConfig')
        self.config = config
        self.user_config = user_config
        self.cp = configparser.ConfigParser(allow_no_value=True)
        self.ucp = configparser.ConfigParser(allow_no_value=True)
        self.setup()
        self.__get_config()

    def setup(self):
        if not os.path.isfile(self.config):
            self.logger.send_message('error', 'Missing Required default config file:: {}'.format(self.config), True)
        if not os.path.isfile(self.user_config):
            self.setup_user_config_defaults()

    def __get_config(self):
        self.cp.read(self.config)
        self.ucp.read(self.user_config)

    def reload_config(self):
        self.__get_config()
        self.get_active_log_files()


    def setup_user_config_defaults(self):
        message = 'Initial Setup of SumoLogic'
        self.logger.send_message(mtype='info', message=message, stop=False)
        self.ucp.add_section('default')
        self.ucp.set('default', 'debug', 'False')
        self.ucp.add_section('apache')
        self.ucp.set('apache', '; comma separated list of apache access log files')
        self.ucp.set('apache', 'apache_access_logs', '[]')
        self.ucp.set('apache', '; comma separated list of apache error log files')
        self.ucp.set('apache', 'apache_error_logs', '[]')

        self.ucp.add_section('mysql')
        self.ucp.set('mysql', 'mysql_log_path', '')

        self.ucp.add_section('sumo_info')
        self.ucp.set('sumo_info', '; Leaving an endpoint empty disable data collection for that endpoint')
        self.ucp.set('sumo_info', '; list, [], of apache endpoints for each of the hosts defined above')
        self.ucp.set('sumo_info', '; if the list has one entry then it will send all access logs to that endpoint')
        self.ucp.set('sumo_info', 'apache_access_endpoints', '')
        self.ucp.set('sumo_info', '; if the list has one entry then it will send all error logs to that endpoint')
        self.ucp.set('sumo_info', '; list, [], of apache endpoints for each of the hosts defined above')
        self.ucp.set('sumo_info', 'apache_error_endpoints', '')
        self.ucp.set('sumo_info', 'mysql_log_endpoint', '')
        self.ucp.set('sumo_info', 'mysql_processes_endpoint', '')
        self.ucp.set('sumo_info', 'syslog_endpoint', '')
        self.ucp.set('sumo_info', 'dpkg_endpoint', '')
        self.ucp.set('sumo_info', 'apt_endpoint', '')
        self.ucp.set('sumo_info', 'auth_endpoint', '')
        self.ucp.set('sumo_info', 'cron_endpoint', '')
        self.ucp.set('sumo_info', 'daemon_endpoint', '')
        self.ucp.set('sumo_info', 'mail_warn_endpoint', '')
        self.ucp.set('sumo_info', 'mail_error_endpoint', '')
        self.ucp.set('sumo_info', 'messages_endpoint', '')
        self.ucp.set('sumo_info', 'user_endpoint', '')
        try:
            with open(self.user_config, 'w') as cfh:
                self.ucp.write(cfh)
        except Exception as e:
            message = 'Failure creating default sumo config file {}: {} | {}'.format(
                e.__class__,
                e,
                traceback.print_exc()
            )
            self.logger.send_message(mtype='error', message=message, stop=True)
    
    def get_value(self, section, option):
        value = None
        if self.cp.has_section(section) and self.cp.has_option(section, option):
            value = self.cp.get(section, option)
        # user config overrides default
        if self.ucp.has_section(section) and self.ucp.has_option(section, option):
            value = self.ucp.get(section, option)
        return value

    def __get_apache_log_files(self, option):
        apache_files = self.ucp.get(
            'apache',
            option.replace('endpoint', 'log')
        ).strip().lstrip('[').rstrip(']').split(',')
        log_files = []
        if len(apache_files) > 0:
            for apache_log_file in apache_files:
                log_file = apache_log_file.strip()
                if log_file.startswith('"') or log_file.startswith("'"):
                    log_file = log_file[1:-1]
                log_files.append(log_file)
        return log_files

    def __get_apache_log_file(self, key, index):
        apache_files = self.ucp.get(
            'apache',
            key.replace('endpoint', 'log')
        ).strip().lstrip('[').rstrip(']').split(',')
        log_file = None
        if len(apache_files) > index and apache_files[index]:
            log_file = apache_files[index].strip()
            if log_file.startswith('"') or log_file.startswith("'"):
                log_file = log_file[1:-1]
        return log_file

    def __get_log_file(self, search_endpoint):
        search_option = search_endpoint.replace('endpoint', 'log')
        # loop over user sections
        log_file = self.__get_user_log_file_setting(search_option)
        if log_file is None:
            log_file = self.__get_default_log_file_setting(search_option)
        return log_file

    def __get_default_log_file_setting(self, search_option):
        log_file = None
        # loop over default sections
        for section in self.cp.sections():
            # loop over options
            if self.cp.has_option(section, search_option):
                # set value if it exists
                log_file = self.get_value(section, search_option)
                break
        return log_file

    def __get_user_log_file_setting(self, searchkey):
        log_file = None
        # loop over default sections
        for section in self.ucp.sections():
            # loop over keys
            if searchkey in self.ucp[section]:
                # set value if it exists
                log_file = self.get_value(section, searchkey)
        return log_file

    def get_active_log_files(self):
        self.active_endpoints = []
        sumo_info = self.ucp['sumo_info']
        for key in sumo_info:
            endpoint = self.get_value('sumo_info', key)
            if endpoint == '' or endpoint is None:
                continue
            if key.startswith('apache'):
                self.__set_apache_endpoint(key, endpoint)
            else:
                log_file = self.__get_log_file(key)
                self.__set_endpoint(key, endpoint, log_file)
        return self.active_endpoints

    def __set_apache_endpoint(self, option, endpoint):
        apache_endpoints = endpoint.strip().lstrip('[').rstrip(']').split(',')

        if len(apache_endpoints) > 1:
            for apache_index in range(0, len(apache_endpoints)):
                apache_endpoint = apache_endpoints[apache_index].strip()
                if apache_endpoint.startswith('"') or apache_endpoint.startswith("'"):
                    apache_endpoint = apache_endpoint[1:-1]
                etype = '{}-{}'.format(option, apache_index)
                log_file = self.__get_apache_log_file(option, apache_index)
                self.__set_endpoint(etype, apache_endpoint, log_file)
        else:
            apache_endpoint = apache_endpoints[0].strip()
            if apache_endpoint.startswith('"') or apache_endpoint.startswith("'"):
                apache_endpoint = apache_endpoint[1:-1]

            apache_log_files = self.__get_apache_log_files(option)
            for apache_index in range(0, len(apache_log_files)):
                etype = '{}-{}'.format(option, apache_index)
                log_file = self.__get_apache_log_file(option, apache_index)
                self.__set_endpoint(etype, apache_endpoint, log_file)

    def __set_endpoint(self, etype, endpoint, log_file):
        self.active_endpoints.append(
            {
                'type': etype,
                'endpoint': endpoint,
                'log_file': log_file,
                'offset_file': '{}.offset'.format(etype)
            }
        )
