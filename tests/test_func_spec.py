from __future__ import absolute_import

import unittest

import hammock.types.func_spec as func_spec
import hammock.converters as converters


def test_func(  # pylint: disable=unused-argument
    an_int,
    a_string,
    an_arg_without_type,
    dict_arg,
    a_default_bool=None,
    a_default_bool_true=True,
    a_default_bool_false=False,
    **kwargs_parameter
):
    """
    This is a test function
    Second line doc
    :param int an_int: integer value.
    :param str a_string: string value.
        second line doc
    :param an_arg_without_type: no type here...
    :param dict dict_arg: some dict argument.
    :param bool a_default_bool: a boolean value with default True.
    :param bool[True] a_default_bool_true: a boolean value with default True.
    :param bool[False] a_default_bool_false: a boolean value with default True.
    :param kwargs_parameter: some more arguments.
    :return dict: return value
    """
    pass


class TestFuncSpec(unittest.TestCase):

    def test_func_spec(self):
        spec = func_spec.FuncSpec(test_func)

        self.assertListEqual(spec.args, ['an_int', 'a_string', 'an_arg_without_type', 'dict_arg'])
        self.assertDictEqual(spec.kwargs, {
            'a_default_bool': None,
            'a_default_bool_true': True,
            'a_default_bool_false': False,
        })

        self.assertEqual(spec.doc, '\nThis is a test function\nSecond line doc')

        self.assertEqual(spec.args_info['an_int'].convert, converters.to_int)
        self.assertEqual(spec.args_info['a_string'].convert, converters.to_str)
        self.assertEqual(spec.args_info['a_default_bool'].convert, converters.to_bool)
        self.assertEqual(spec.args_info['a_default_bool_true'].convert, converters.to_bool)
        self.assertEqual(spec.args_info['a_default_bool_false'].convert, converters.to_bool)
        self.assertEqual(spec.args_info['a_default_bool'].type_name, 'bool')
        self.assertEqual(spec.args_info['a_default_bool_true'].type_name, 'bool[True]')
        self.assertEqual(spec.args_info['a_default_bool_false'].type_name, 'bool[False]')
        self.assertEqual(spec.args_info['dict_arg'].convert, converters.to_dict)
        self.assertEqual(spec.args_info['kwargs_parameter'].convert, converters.to_dict)

        self.assertEqual(spec.args_info['an_int'].doc, 'integer value.')
        self.assertEqual(spec.args_info['a_string'].doc, 'string value.\nsecond line doc')

        self.assertEqual(spec.returns.convert, converters.to_dict)
        self.assertEqual(spec.returns.doc, 'return value')
