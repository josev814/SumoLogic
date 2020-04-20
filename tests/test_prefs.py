from os.path import dirname, join as ospj, isfile
from os import remove
import unittest
from SumoLogic.prefs import SumoConfig


class SumoConfigTest(unittest.TestCase):
    """
    Base class of all Sync test classes that use a mock sync server.
    """
    def setUp(self):
        self.DIRECTORY = dirname(__file__)
        self.SUMO_DIR = ospj(self.DIRECTORY, 'data', 'sumo_logic')
        self.WORK_DIR = ospj(self.SUMO_DIR, 'work')
        self.ETC_DIR = ospj(self.SUMO_DIR, 'etc')
        self.default_config = ospj(self.ETC_DIR, 'config')
        self.user_config = ospj(self.ETC_DIR, 'user_overrides')
        self.sumoconfig = SumoConfig(self.default_config, self.user_config)
        self.assertTrue(isfile(self.default_config))
        self.assertTrue(isfile(self.user_config))


class SumoConfigDefaults(SumoConfigTest):
    def setUp(self):
        SumoConfigTest.setUp(self)

    def test_get_config_value_wrong_section(self):
        self.assertIsNone(self.sumoconfig.get_value('defaults', 'debug'))

    def test_get_config_value_wrong_setting(self):
        self.assertIsNone(self.sumoconfig.get_value('default', 'debugs'))

    def test_get_config_value(self):
        self.assertEqual(self.sumoconfig.get_value('default', 'work_dir'), '/var/lib/work_dir')


class UserOverrideTests(SumoConfigTest):
    def setUp(self):
        SumoConfigTest.setUp(self)

    def test_01_get_config_value_default_override(self):
        self.assertEqual(self.sumoconfig.get_value('default', 'debug'), 'False')

    def change_entry(self):
        self.sumoconfig.ucp.set('default', 'debug', 'True')
        self.save_to_local_cache()

    def override_entry(self):
        if not self.sumoconfig.ucp.has_section('system_logs'):
            self.sumoconfig.ucp.add_section('system_logs')
        self.sumoconfig.ucp.set('system_logs', 'syslog_log', '/var/log/system')
        self.sumoconfig.ucp.set('sumo_info', 'syslog_endpoint', 'http://google.com/endpoint')
        self.save_to_local_cache()

    def write_new_entry(self):
        self.sumoconfig.ucp.add_section('new_section')
        self.sumoconfig.ucp.set('new_section', 'new_option', 'True')
        self.save_to_local_cache()

    def save_to_local_cache(self):
        with open(self.sumoconfig.user_config, 'w') as uch:
            self.sumoconfig.ucp.write(uch)

    def test_02_reload(self):
        self.assertIsNone(self.change_entry())
        self.assertIsNone(self.override_entry())
        self.assertIsNone(self.write_new_entry())
        self.assertIsNone(self.sumoconfig.reload_config())
        self.assertEqual(self.sumoconfig.get_value('default', 'debug'), 'True')
        self.assertEqual(self.sumoconfig.get_value('new_section', 'new_option'), 'True')
        self.assertEqual(self.sumoconfig.get_value('system_logs', 'syslog_log'), '/var/log/system')

    def test_03_get_active_endpoints_none_set(self):
        self.assertIsInstance(self.sumoconfig.get_active_log_files(), type([]))
        self.assertListEqual(self.sumoconfig.get_active_log_files(), [])

    def set_active_endpoints(self):
        self.sumoconfig.ucp.set('sumo_info', 'syslog_endpoint', 'https://github.com')
        self.sumoconfig.ucp.set('sumo_info', 'dpkg_endpoint', 'https://github2.com')

    def test_04_get_active_endpoints(self):
        self.set_active_endpoints()
        active_logs = self.sumoconfig.get_active_log_files()
        self.assertEqual(len(active_logs), 2)
        self.assertDictEqual(
            active_logs[0],
            {
                'type': 'syslog_endpoint',
                'endpoint': 'https://github.com',
                'log_file': '/var/log/syslog',
                'offset_file': 'syslog_endpoint.offset'
            }
        )
        self.assertDictEqual(
            active_logs[1],
            {
                'type': 'dpkg_endpoint',
                'endpoint': 'https://github2.com',
                'log_file': '/var/log/dpkg.log',
                'offset_file': 'dpkg_endpoint.offset'
            }
        )

    def set_apache_endpoints(self):
        self.sumoconfig.ucp.set('sumo_info', 'apache_access_endpoints', '{}'.format(['https://github-access.com']))
        self.sumoconfig.ucp.set('sumo_info', 'apache_error_endpoints', '{}'.format(['https://github-error.com']))

    def set_apache_log_areas(self):
        self.sumoconfig.ucp.set('apache', 'apache_access_logs', '{}'.format(['/var/log/apache2/github-access-log']))
        self.sumoconfig.ucp.set('apache', 'apache_error_logs', '{}'.format(['/var/log/apache2/github-error-log']))

    def test_05_get_apache_endpoints_none(self):
        active_logs = self.sumoconfig.get_active_log_files()
        self.assertEqual(len(active_logs), 0)

    def test_06_get_apache_endpoints_2(self):
        self.set_apache_log_areas()
        self.set_apache_endpoints()
        self.save_to_local_cache()
        active_logs = self.sumoconfig.get_active_log_files()
        self.assertEqual(len(active_logs), 2)

    def set_extra_apache_endpoints(self):
        self.sumoconfig.ucp.set('sumo_info', 'apache_access_endpoints', '{}'.format(['https://github-access.com', 'https://google-access.com']))
        self.sumoconfig.ucp.set('sumo_info', 'apache_error_endpoints', '{}'.format(['https://github-error.com', 'https://google-error.com']))

    def set_extra_apache_log_areas(self):
        self.sumoconfig.ucp.set('apache', 'apache_access_logs', '{}'.format(['/var/log/apache2/github-access-log', '/var/log/apache2/google-access-log']))
        self.sumoconfig.ucp.set('apache', 'apache_error_logs', '{}'.format(['/var/log/apache2/github-error-log', '/var/log/apache2/google-error-log']))

    def test_07_get_apache_endpoints_4(self):
        self.sumoconfig = SumoConfig(self.default_config, self.user_config)
        self.set_extra_apache_log_areas()
        self.set_extra_apache_endpoints()
        self.save_to_local_cache()
        active_logs = self.sumoconfig.get_active_log_files()
        self.assertEqual(len(active_logs), 4)

    def tearDown(self):
        if isfile(self.default_config):
            remove(self.default_config)
        if isfile(self.user_config):
            remove(self.user_config)
        pass
