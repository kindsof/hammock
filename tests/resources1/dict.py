from __future__ import absolute_import
import six
import hammock
import hammock.exceptions as exceptions


class KeyNotFound(exceptions.NotFound):
    def __init__(self):  # pylint: disable=super-on-old-class
        super(KeyNotFound, self).__init__('Key not found')


class Dict(hammock.Resource):

    POLICY_GROUP_NAME = False

    def __init__(self, *args, **kwargs):
        super(Dict, self).__init__(*args, **kwargs)
        self._dict = {}

    @hammock.post("{key}", success_code=201)
    def insert(self, key, value):  # pylint: disable=unused-argument
        """
        Create a new key-value pair
        :param key: key to insert
        :param value: a value to the key
        :return dict: the created key-value
        """
        if key in self._dict:
            raise exceptions.BadRequest('Key already exists')
        self._dict[key] = value
        return {'key': key, 'value': value}

    @hammock.get("{key}")
    def get(self, key, default=None):  # pylint: disable=unused-argument
        """
        Get a value from the dict
        :param key: which key to get
        :return dict: the key: value
        """
        if default is None and key not in self._dict:
            raise KeyNotFound()
        return {'key': key, 'value': self._dict.get(key, default)}

    @hammock.get()
    def list(self):
        """
        Show all the dict
        :return list: the content of the dict
        """
        return [{'key': key, 'value': value} for key, value in six.iteritems(self._dict)]

    @hammock.put("{key}")
    def update(self, key, value):  # pylint: disable=unused-argument
        """
        Update an existing key
        :param key: a key to update
        :param value: new value for the key
        :return dict: the old key: value
        """
        if key not in self._dict:
            raise KeyNotFound()
        old_value = self._dict[key]
        self._dict[key] = value
        return {'key': key, 'value': old_value}

    @hammock.delete("{key}")
    def remove(self, key):  # pylint: disable=unused-argument
        """
        Deletes a key from the dict
        :param key: which key to delete
        :return dict: the old key: value
        """
        if key not in self._dict:
            raise KeyNotFound()
        value = self._dict[key]
        del self._dict[key]
        return {'key': key, 'value': value}
