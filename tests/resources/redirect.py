from __future__ import absolute_import
import codecs
import json
from hammock import resource
from hammock import common
from hammock import types

PORT = 12345
DEST = "http://localhost:{:d}".format(PORT)


def pre_manipulate(request, _):
    body = json.load(codecs.getreader('utf-8')(request.stream))
    body['some_more_data'] = 'b'
    request.set_content(json.dumps(body))


def post_manipulate(response, _):
    body = common.get_response_json(response)
    assert body['body'].pop('some_more_data') == 'b'
    body = json.dumps(body)
    headers = types.Headers(response.headers)
    headers[common.CONTENT_LENGTH] = str(len(body))
    return types.Response(body, headers, response.status)


def pre_manipulate_path(request, _):
    request.path = 'a'


def post_manipulate_path(response, _):
    body = common.get_response_json(response)
    assert body['path'] == '/a'
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
        pre_process=pre_manipulate,
        post_process=post_manipulate,
    )
    def post_passthrough(self):
        pass

    @resource.post_passthrough(
        dest=None,
        path='post-passthrough-with-body',
        trim_prefix='redirect',
        pre_process=pre_manipulate,
        post_process=post_manipulate,
    )
    def post_passthrough_with_body(self, request):
        body = json.dumps(dict(
            body=json.loads(request.stream),
            headers=dict(request.headers),
        ))
        return types.Response(
            body,
            {
                common.CONTENT_LENGTH: str(len(body)),
                common.CONTENT_TYPE: common.TYPE_JSON
            },
            200
        )

    @resource.get_passthrough(
        dest=DEST,
        path='manipulate-path',
        trim_prefix='redirect',
        pre_process=pre_manipulate_path,
        post_process=post_manipulate_path,
    )
    def manipulate_path(self):
        pass
