from __future__ import absolute_import
import hammock
from hammock import types

PORT = 12345
DEST = "http://localhost:{:d}".format(PORT)


def pre_manipulate(request, _):
    body = request.json
    body['some_more_data'] = 'b'
    request.json = body


def post_manipulate(response, _):
    body = response.json
    assert body['body'].pop('some_more_data') == 'b'
    response.json = body


def pre_manipulate_path(request, _):
    request.path = 'a'


def post_manipulate_path(response, _):
    body = response.json
    assert body['path'] == '/a'
    response.json = body


class Redirect(hammock.Resource):

    POLICY_GROUP_NAME = False

    @hammock.sink(dest=DEST, trim_prefix="redirect")
    def passthrough(self):
        pass

    @hammock.get("specific")
    def specific(self):
        return "specific"

    @hammock.post(
        dest=DEST,
        path='post-passthrough',
        trim_prefix='redirect',
        pre_process=pre_manipulate,
        post_process=post_manipulate,
    )
    def post_passthrough(self):
        pass

    @hammock.post(
        dest=None,
        path='post-passthrough-with-body',
        trim_prefix='redirect',
        pre_process=pre_manipulate,
        post_process=post_manipulate,
    )
    def post_passthrough_with_body(self, request):
        body = {
            'body': request.json,
            'headers': dict(request.headers),
        }
        return types.Response(content=body)

    @hammock.get(
        dest=DEST,
        path='manipulate-path',
        trim_prefix='redirect',
        pre_process=pre_manipulate_path,
        post_process=post_manipulate_path,
    )
    def manipulate_path(self):
        pass
