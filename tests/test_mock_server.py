# Third-party imports...
from unittest import TestCase

# Local imports...
from .mock_server import MockServer
import time


class TestMockServer(TestCase):

    # def setup_class(self):
    def setUp(self):
        self.mock_server = MockServer()
        self.assertTrue(
            self.mock_server.start_mock_server()
        )

    def test_01_ensure_server_running(self):
        self.assertTrue(self.mock_server.is_server_running())

    def test_02_validate_server_port(self):
        self.port = self.mock_server.port
        self.assertNotEqual(self.port, 0)

    def test_99_teardown_server(self):
        self.assertFalse(self.mock_server.is_server_running())

    """    def test_request_response(self):
        mock_endpoint_url = 'http://localhost:{port}/receiver/v1/http/'.format(port=self.port)

        # Patch USERS_URL so that the service uses the mock server URL instead of the real URL.
        with patch.dict('project.services.__dict__', {'USERS_URL': mock_endpoint_url}):
            response = get_users()

        assert_dict_contains_subset({'Content-Type': 'application/json; charset=utf-8'}, response.headers)
        assert_true(response.ok)
        assert_list_equal(response.json(), [])
    """
