from __future__ import absolute_import
import io
import hammock
import falcon


class Files(hammock.Resource):

    POLICY_GROUP_NAME = False

    @hammock.post(response_content_type=hammock.TYPE_OCTET_STREAM)
    def echo(self, _file):
        data = _file.stream.read()
        return io.BytesIO(data)

    @hammock.get(response_content_type=hammock.TYPE_OCTET_STREAM)
    def generate(self, size_mb):
        return io.BytesIO(bytearray(int(size_mb) << 20))

    @hammock.post("check_size")
    def check_size(self, _file, size_mb):
        size_mb = int(size_mb)
        actual_size = _file.stream.read().__sizeof__() >> 20
        if actual_size != size_mb:
            raise falcon.HTTPError(
                falcon.HTTP_400,
                "Wrong file size"
                "Got {:d}mb, expected more than {:d}mb".format(actual_size, size_mb)
            )
        return "OK"
