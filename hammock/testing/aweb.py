from __future__ import absolute_import
import six
import logging
import asyncio
import mock
import unittest
from aiohttp import protocol
from aiohttp import streams
import hammock.common as common


LOG = logging.getLogger(__name__)


class Transport(mock.MagicMock):
    def __init__(self, *args, **kwargs):
        super(Transport, self).__init__(*args, **kwargs)
        self.content = []

    def write(self, content):
        self.content.append(content)

    def get_extra_info(self, key):
        return {
            'sslcontext': False,
        }.get(key, mock.MagicMock())


class AWebTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(AWebTest, self).__init__(*args, **kwargs)
        self.api = None
        self.srmock = None

    def setUp(self):
        self.api = 'aiohttp'
        self.srmock = mock.MagicMock()
        self.before(debug=True, logger=LOG)

    def before(self, **kwargs):
        pass

    def simulate_request(self, url, method, query_string=None, body=None, headers=None):
        assert url.startswith('/'), "path must start with '/'"
        handler_factory = self.hammock.api.make_handler()
        loop = asyncio.get_event_loop()
        path = url + (('?' + query_string) if query_string else '')
        transport = Transport()
        message = protocol.Request(transport, method, path)
        message.add_headers(*list(headers.items()))
        message.should_close = True
        payload = streams.StreamReader()
        if body is not None:
            if isinstance(body, six.string_types):
                body = body.encode(common.ENCODING)
            payload.feed_data(body)
        handler = handler_factory()
        handler.connection_made(transport)

        # Run the dispatcher and fetch response into transport.content.
        loop.run_until_complete(handler.handle_request(message, payload))

        status, headers, stream = self._extract_from_response(transport.content)
        self.srmock.status = status
        self.srmock.headers = headers
        return stream

    def _extract_from_response(self, content):
        header = content[0].decode(common.ENCODING)
        stream = content[1:]
        status_line, headers = header.split('\r\n', 1)
        status = self._status_line_to_status_code(status_line)
        headers = dict([
            line.split(': ')
            for line in headers.split('\r\n')
            if ':' in line
        ])
        if headers.get('TRANSFER-ENCODING') == 'chunked':
            stream = [chunk[:-2].split(b'\r\n')[1] for chunk in stream]
        return status, headers, stream

    def _status_line_to_status_code(self, status_line):
        """
        :param status_line: a status line, like HTTP/1.1 404 Not Found
        :return: status code, 404 for the above example
        """
        return status_line.split(' ', 2)[1]
