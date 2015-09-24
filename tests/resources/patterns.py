from hammock import resource
from hammock import types
import StringIO


class Patterns(resource.Resource):
    @resource.get()
    def get(self):
        return "base"

    @resource.get("{my_id}")
    def get_id(self, my_id):
        return "id-%s" % my_id

    @resource.sink("{my_id}/extra")
    def get_id_metadata(self, request, my_id):  # pylint: disable=unused-argument
        return types.Response(
            stream=StringIO.StringIO('"extra-%s"' % my_id),
            status=200,
            headers={}
        )
