from __future__ import absolute_import
import six
import threading
import logging
try:
    import ujson as json
except ImportError:
    import json
import socket
import hammock.common as common


def test_connection(address):
    try:
        socket.create_connection(address)
    except socket.error:
        return False
    else:
        return True


def get_available_port():
    sock = socket.socket()
    sock.bind(("", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


class Server(object):
    def __init__(self, host="localhost", port=None, name=None):
        self.host = host
        self.port = port or get_available_port()
        logging.info("Starting server on %s:%d...", self.host, self.port)
        self.name = name
        self._httpd = _Server((self.host, self.port), type("Handler", (Handler, object), {"name": self.name}))
        self._thread = threading.Thread(target=self._httpd.serve_forever)
        self._thread.start()
        logging.info("Server started")

    def close(self):
        logging.info("Closing server...")
        self._httpd.shutdown()
        self._httpd.server_close()
        logging.info("Server closed")


class _Server(six.moves.socketserver.TCPServer):
    allow_reuse_address = True


class Handler(six.moves.SimpleHTTPServer.SimpleHTTPRequestHandler):
    name = None

    def log_message(self, formatting, *args):
        # Quite output of SimpleHttpServer
        logging.debug(
            "%s - - [%s] %s",
            self.client_address[0], self.log_date_time_string(), formatting % args)

    def __init__(self, *args, **kwargs):
        self.path = None
        six.moves.SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, *args, **kwargs)

    def do_GET(self):  # NOQA  # pylint: disable=invalid-name
        self._do("GET")

    def do_DELETE(self):  # NOQA  # pylint: disable=invalid-name
        self._do("DELETE")

    def do_POST(self):  # NOQA  # pylint: disable=invalid-name
        self._do("POST")

    def do_PUT(self):  # NOQA  # pylint: disable=invalid-name
        self._do("PUT")

    def _do(self, method):
        if common.CONTENT_LENGTH in self.headers \
                and int(self.headers[common.CONTENT_LENGTH]) > 0 \
                and method in ("PUT", "POST"):
            body = self.rfile.read(int(self.headers[common.CONTENT_LENGTH]))
        else:
            body = None
        if body and not isinstance(body, six.string_types):
            body = body.decode()
        if common.TYPE_JSON in self.headers.get(common.CONTENT_TYPE, ''):
            body = json.loads(body)
        parsed = six.moves.urllib.parse.urlsplit(self.path)
        content = dict(
            method=method,
            path=parsed.path,
            headers=dict(self.headers.items()),
            query_string=parsed.query,
            body=body,
        )
        content['server_name'] = self.__class__.name
        logging.info("Server echoing: %s", content)
        self.send_response(200)
        if not self.headers.get(common.CONTENT_TYPE) or common.TYPE_JSON in self.headers[common.CONTENT_TYPE]:
            if isinstance(content, six.binary_type):
                content = content.decode()  # pylint: disable=no-member
            content = six.b(json.dumps(content))
            self.send_header(common.CONTENT_LENGTH, len(content))
            self.send_header(common.CONTENT_TYPE, common.TYPE_JSON)
            self.end_headers()
            self.wfile.write(content)
        else:
            content = six.b(body)
            self.send_header(common.CONTENT_LENGTH, len(content))
            self.send_header(common.CONTENT_TYPE, common.TYPE_OCTET_STREAM)
            self.end_headers()
            self.wfile.write(content)
        self.wfile.flush()
