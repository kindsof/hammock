from __future__ import absolute_import
import json
from hammock import resource
from hammock import common
from hammock import types


PORT = 12345
DEST = "http://localhost:{:d}".format(PORT)


def pre_manipulate(request, _):
    body = json.load(request.stream)
    body['some_more_data'] = 'b'
    common.set_request_body(request, json.dumps(body))


def post_manipulate(response, _):
    body = common.get_response_json(response)
    inner_body = json.loads(body['body'])
    assert inner_body.pop('some_more_data') == 'b'
    body['body'] = json.dumps(inner_body)
    body = json.dumps(body)
    headers = types.Headers(response.headers)
    headers[common.CONTENT_LENGTH] = str(len(body))
    return types.Response(body, headers, response.status)


class Redirect(resource.Resource):

    @resource.passthrough(dest=DEST, trim_prefix="redirect")
    def passthrough(self):
        pass

    @resource.get("specific")
    def specific(self):
        return "specific"

    @resource.post_passthrough(
        dest=DEST,
        path='post-passthrough',
        trim_prefix='redirect',
        post_process=post_manipulate,
        pre_process=pre_manipulate,
    )
    def post_passthrough(self):
        pass

    @resource.post_passthrough(
        dest=None,
        path='post-passthrough-with-body',
        trim_prefix='redirect',
        post_process=post_manipulate,
        pre_process=pre_manipulate,
    )
    def post_passthrough_with_body(self, request):
        body = json.dumps(dict(
            body=json.loads(request.stream),
            headers=request.headers,
        ))
        return types.Response(
            body,
            {
                common.CONTENT_LENGTH: str(len(body)),
                common.CONTENT_TYPE: common.TYPE_JSON
            },
            200
        )
