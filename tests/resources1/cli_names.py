from __future__ import absolute_import
import hammock

NAMES = {
    'name_with_underscores': 'name-with-underscores',
    'NameWithCamelCase': 'name-with-camel-case',
    'MULTICaps': 'multi-caps',
}


class CLINames(hammock.Resource):
    POLICY_GROUP_NAME = False


def _get_func(func_name):
    @hammock.get(func_name)
    def func(self):  # pylint: disable=unused-argument
        return func_name
    func.__name__ = func_name
    return func

for name in NAMES.keys():
    setattr(CLINames, name, _get_func(name))
