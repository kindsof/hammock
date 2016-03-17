from __future__ import absolute_import
import hammock
import hammock.exceptions as exceptions


class NotFound(exceptions.NotFound):
    def __init__(self):  # pylint: disable=super-on-old-class
        super(NotFound, self).__init__('Item not found')


class List(hammock.Resource):

    POLICY_GROUP_NAME = False

    def __init__(self, *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)
        self._list = []

    @hammock.post(success_code=201)
    def append(self, value):
        """
        Append a value
        :param value: a value to a append to the list
        """
        self._list.append(value)

    @hammock.delete('{value}')
    def remove(self, value):
        """
        Remove a value from the list
        :param value: a value to remove
        """
        try:
            self._list.remove(value)
        except ValueError:
            raise NotFound()

    @hammock.get()
    def list(self):
        """
        Show all the list
        :return list: the content of the list
        """
        return self._list
