from __future__ import absolute_import
import hammock


class ArgumentTypes(hammock.Resource):

    POLICY_GROUP_NAME = False

    @hammock.get()
    def conversions_in_get(self, a_list, an_int, a_float, a_bool, a_string, not_in_doc):  # pylint: disable=unused-argument
        """
        Check conversion of argument in URL methods.
        :param str a_string: a string argument
        :param bool a_bool: a bool argument
        :param float a_float: a float argument
        :param int an_int: an int argument
        :param list a_list: a list argument
        :return bool: True if all arguments have the correct type
        """
        return all([
            isinstance(a_list, list),
            isinstance(an_int, int),
            isinstance(a_float, float),
            isinstance(a_bool, bool),
            isinstance(a_string, str),
        ])

    @hammock.get('with-default')
    def conversions_in_get_with_default(  # pylint: disable=unused-argument
            self, a_list=None, an_int=1, a_float=0.1, a_bool=True, a_string='123', not_in_doc=None):
        """
        Check conversion of argument in URL methods.
        :param str a_string: a string argument
        :param bool a_bool: a bool argument
        :param float a_float: a float argument
        :param int an_int: an int argument
        :param list a_list: a list argument
        :return bool: True if all arguments have the correct type
        """
        return all([
            isinstance(a_list, list),
            isinstance(an_int, int),
            isinstance(a_float, float),
            isinstance(a_bool, bool),
            isinstance(a_string, str),
        ])

    @hammock.get('to-list')
    def get_to_list(self, a_list):
        """
        Check conversion of argument in URL methods.
        :param list a_list: a list argument
        :return list: the list
        """
        return a_list
