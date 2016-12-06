from __future__ import absolute_import
import hammock
import uuid


class ArgumentTypes(hammock.Resource):

    POLICY_GROUP_NAME = False

    @hammock.get()
    def conversions_in_get(self, a_list, an_int, a_float, a_bool, a_string, a_uuid, not_in_doc):  # pylint: disable=unused-argument
        """
        Check conversion of argument in URL methods.
        :param str a_string: a string argument
        :param uuid a_uuid: an uuid argument
        :param bool a_bool: a bool argument
        :param float a_float: a float argument
        :param int an_int: an int argument
        :param list a_list: a list argument
        :return bool: True if all arguments have the correct type
        """
        if not isinstance(a_list, list):
            raise hammock.exceptions.BadRequest('a_list is not a list')
        if not isinstance(an_int, int):
            raise hammock.exceptions.BadRequest('an_int is not an int')
        if not isinstance(a_float, float):
            raise hammock.exceptions.BadRequest('a_float is not a float')
        if not isinstance(a_bool, bool):
            raise hammock.exceptions.BadRequest('a_bool is not a bool')
        if not isinstance(a_string, str):
            raise hammock.exceptions.BadRequest('a_string is not a string')
        try:
            if not isinstance(a_uuid, str):
                raise ValueError("a_uuid is not a string")
            uuid.UUID(a_uuid)
        except ValueError:
            raise hammock.exceptions.BadRequest('a_uuid is not a uuid')
        return True

    @hammock.get('with-default')
    def conversions_in_get_with_default(  # pylint: disable=unused-argument
            self, a_list=None, an_int=1, a_float=0.1, a_bool=True, a_string='123', a_uuid='ceae3dd0-5a38-4189-b65c-bbb66a457812', not_in_doc=None):
        """
        Check conversion of argument in URL methods.
        :param str a_string: a string argument
        :param uuid a_uuid: an uuid argument
        :param bool a_bool: a bool argument
        :param float a_float: a float argument
        :param int an_int: an int argument
        :param list a_list: a list argument
        :return bool: True if all arguments have the correct type
        """
        if not isinstance(a_list, list):
            raise hammock.exceptions.BadRequest('a_list is not a list')
        if not isinstance(an_int, int):
            raise hammock.exceptions.BadRequest('an_int is not an int')
        if not isinstance(a_float, float):
            raise hammock.exceptions.BadRequest('a_float is not a float')
        if not isinstance(a_bool, bool):
            raise hammock.exceptions.BadRequest('a_bool is not a bool')
        if not isinstance(a_string, str):
            raise hammock.exceptions.BadRequest('a_string is not a string')
        try:
            if not isinstance(a_uuid, str):
                raise ValueError
            uuid.UUID(a_uuid)
        except ValueError:
            raise hammock.exceptions.BadRequest('a_uuid is not a uuid')
        return True

    @hammock.get('to-list')
    def get_to_list(self, a_list):
        """
        Check conversion of argument in URL methods.
        :param list a_list: a list argument
        :return list: the list
        """
        return a_list
