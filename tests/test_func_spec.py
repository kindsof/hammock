from __future__ import absolute_import
import unittest
import hammock.types.func_spec as func_spec


def test_func(an_int, a_string, an_arg_without_type, a_default_bool=True, **kwargs_parameter):  # pylint: disable=unused-argument
    """
    This is a test function
    Second line doc
    :param int an_int: integer value.
    :param str a_string: string value.
        second line doc
    :param an_arg_without_type: no type here...
    :param bool a_default_bool: a boolean value with default True.
    :param kwargs_parameter: some more arguments.
    :return dict: return value
    """
    pass


class TestFuncSpec(unittest.TestCase):

    def test_func_spec(self):
        spec = func_spec.FuncSpec(test_func)

        self.assertListEqual(spec.args, ['an_int', 'a_string', 'an_arg_without_type'])
        self.assertDictEqual(spec.kwargs, {'a_default_bool': True})

        self.assertEqual(spec.doc, '\nThis is a test function\nSecond line doc')

        self.assertEqual(spec.args_info('an_int').type, int)
        self.assertEqual(spec.args_info('a_string').type, str)
        self.assertEqual(spec.args_info('an_arg_without_type').type, str)
        self.assertEqual(spec.args_info('a_default_bool').type, bool)
        self.assertEqual(spec.args_info('kwargs_parameter').type, dict)

        self.assertEqual(spec.args_info('an_int').doc, 'integer value.')
        self.assertEqual(spec.args_info('a_string').doc, 'string value.\nsecond line doc')

        self.assertEqual(spec.returns.type, dict)
        self.assertEqual(spec.returns.doc, 'return value')
