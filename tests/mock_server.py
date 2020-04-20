# Standard library imports...
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import re
import socket
from threading import Thread

# Third-party imports...
import requests


class MockServerRequestHandler(BaseHTTPRequestHandler):
    HTTP_V1_ENDPOINT_PATTERN = re.compile(r'/receiver/v1/http/')

    def do_GET(self):
        if re.search(self.HTTP_V1_ENDPOINT_PATTERN, self.path):
            # Add response status code.
            self.send_response(requests.codes.ok)

            # Add response headers.
            self.send_header('Content-Type', 'text/html;charset=iso-8859-1')
            self.end_headers()

            # Add response content.
            response_content = json.dumps([])
            self.wfile.write(response_content.encode('iso-8859-1'))
            return


class MockServer(object):
    port = 0
    mock_server = None
    mock_server_thread = None

    def __init__(self):
        self.server_baseurl = 'localhost'

    def get_free_port(self):
        s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
        s.bind((self.server_baseurl, 0))
        address, port = s.getsockname()
        s.close()
        return port

    def start_mock_server(self):
        try:
            self.port = self.get_free_port()
            self.mock_server = HTTPServer(('localhost', self.port), MockServerRequestHandler)
            self.mock_server_thread = Thread(target=self.mock_server.serve_forever)
            self.mock_server_thread.setDaemon(True)
            self.mock_server_thread.start()
        except Exception as e:
            print(e)
            return False
        return True

    def stop_mock_server(self):
        if self.mock_server_thread.isAlive():
            self.mock_server.shutdown()

    def is_server_running(self):
        if self.mock_server_thread.is_alive():
            return True
        return False
