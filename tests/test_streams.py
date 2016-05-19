from __future__ import absolute_import
import tests.base as base
import six
import os
import logging
import hammock.common as common


MB_TO_TEST = 50


class TestStreams(base.TestBase):

    def test_streams(self):
        path = "/files"
        logging.info("Testing post and get of %d mb", MB_TO_TEST)
        body = bytearray(MB_TO_TEST << 20)
        response = self._simulate(
            "POST",
            path,
            body=body,
            headers={
                common.CONTENT_TYPE: common.TYPE_OCTET_STREAM,
                common.CONTENT_LENGTH: str(len(body)),
            },
        )
        if not isinstance(response, six.binary_type):
            body = body.decode()
        self.assertEqual(response, body)

        logging.info("Testing get of %d mb", MB_TO_TEST)
        response = self._simulate(
            "GET",
            path,
            query_string="size_mb={:d}".format(MB_TO_TEST)
        )
        size_bytes = len(response) if not isinstance(response, six.binary_type) else response.__sizeof__()
        self.assertEqual(MB_TO_TEST, size_bytes >> 20)
        logging.info("Testing reading in server of %d mb", MB_TO_TEST)
        response = self._simulate(
            "POST",
            os.path.join(path, "check_size"),
            query_string="size_mb={:d}".format(MB_TO_TEST),
            body=body,
            headers={common.CONTENT_TYPE: common.TYPE_OCTET_STREAM},
        )
        self.assertEqual(response, "OK")
