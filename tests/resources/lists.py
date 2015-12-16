from __future__ import absolute_import
import hammock


class Lists(hammock.Resource):

    @hammock.get('{path}')
    def get(self, path, argument):
        return {
            'path': int(path),
            'argument': [int(ai) for ai in argument],
        }

    @hammock.post('{path}')
    def append(self, path, _list):
        _list.append(int(path))
        return _list
