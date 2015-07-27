from hammock import resource
import StringIO as string_io
import falcon


class Files(resource.Resource):

    @resource.post(response_content_type=resource.TYPE_OCTET_STREAM)
    def echo(self, _file):
        return string_io.StringIO(_file.read())

    @resource.get(response_content_type=resource.TYPE_OCTET_STREAM)
    def generate(self, size_mb):
        return string_io.StringIO(bytearray(int(size_mb) << 20))

    @resource.post("check_size")
    def check_size(self, _file, size_mb):
        size_mb = int(size_mb)
        actual_size = _file.read().__sizeof__() >> 20
        if actual_size != size_mb:
            raise falcon.HTTPError(
                falcon.HTTP_400,
                "Wrong file size"
                "Got {:d}mb, expected more than {:d}mb".format(actual_size, size_mb)
            )
        return "OK"
