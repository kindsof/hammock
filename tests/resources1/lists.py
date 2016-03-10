from __future__ import absolute_import
import hammock


class Lists(hammock.Resource):

    POLICY_GROUP_NAME = False

    @hammock.get('{path}')
    def get(self, path, argument):
        return {
            'path': int(path),
            'argument': [int(ai) for ai in argument],
        }

    @hammock.post('{path}')
    def append(self, path, _list):
        """
        Append to a list
        :param int path: append to list
        :param list _list: list to append to
        :return list: the list with extra value
        """
        _list.append(int(path))
        return _list
