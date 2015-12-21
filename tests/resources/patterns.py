from __future__ import absolute_import
import six
import simplejson as json
import hammock
import hammock.types as types
import hammock.common as common


class Patterns(hammock.Resource):
    @hammock.get()
    def get(self):
        return "base"

    @hammock.get("{my_id}")
    def get_id(self, my_id):
        return "id-%s" % my_id

    @hammock.sink("{my_id}/extra")
    def get_id_metadata(self, request, my_id):  # pylint: disable=unused-argument
        return types.Response(
            stream=six.BytesIO(six.b(json.dumps('extra-%s') % my_id)),
            status=200,
            headers={common.CONTENT_TYPE: common.TYPE_JSON},
        )

    @hammock.sink("{my_id}/extra/specific")
    def get_id_metadata_specific(self, request, my_id):  # pylint: disable=unused-argument
        return types.Response(
            stream=six.BytesIO(six.b(json.dumps('extra-specific-%s') % my_id)),
            status=200,
            headers={common.CONTENT_TYPE: common.TYPE_JSON},
        )
