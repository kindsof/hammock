from __future__ import absolute_import
from hammock import resource


class Lists(resource.Resource):

    @resource.get('{path}')
    def get(self, path, argument):
        return {
            'path': int(path),
            'argument': [int(ai) for ai in argument],
        }

    @resource.post('{path}')
    def append(self, path, _list):
        _list.append(int(path))
        return _list
