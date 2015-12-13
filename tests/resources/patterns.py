from __future__ import absolute_import
import six
import simplejson as json
import hammock.resource as resource
import hammock.types as types
import hammock.common as common


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
            stream=six.moves.StringIO(json.dumps('extra-%s') % my_id),
            status=200,
            headers={common.CONTENT_TYPE: common.TYPE_JSON},
        )
