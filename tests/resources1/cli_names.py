from __future__ import absolute_import
import hammock

NAMES = {
    'name_with_underscores': 'name-with-underscores',
    'NameWithCamelCase': 'name-with-camel-case',
    'MULTICaps': 'multi-caps',
    'CapsMULTI': 'caps-multi',
}


class CLINames(hammock.Resource):
    POLICY_GROUP_NAME = False

    @hammock.post('optional-variable-with-underscore')
    def optional_variable_with_underscores(self, optional_variable=None):
        """
        Returns an optional variable
        :param optional_variable: an optional variable
        :return: the optional variable
        """
        return optional_variable

    @hammock.post('set-true')
    def set_true(self, set_true=False):
        return set_true

    @hammock.post('set-false')
    def set_false(self, set_false=True):
        return set_false

    @hammock.get('ignored-method', cli_command_name=False)
    def ignored_method(self):
        return 'ignored-method'

    @hammock.get('returns-nothing-type')
    def returns_nothing_type(self):
        """
        :return None:
        """
        return 'something'


def _get_func(func_name):
    @hammock.get(func_name)
    def func(self):  # pylint: disable=unused-argument
        return func_name
    func.__name__ = func_name
    return func

for name in NAMES.keys():
    setattr(CLINames, name, _get_func(name))
