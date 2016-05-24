from __future__ import absolute_import
import __builtin__
import mock
import sys
import six


BUILTIN_IMPORT = __builtin__.__import__


def mock_import(packages_to_raise=None):
    """
    Mocks import statement, and squashes ImportErrors
    :param prefixes_to_raise: a list of prefixes to raise ImportError for those modules
    :return: mocking object
    """
    packages_to_raise = packages_to_raise or set()
    packages_to_raise = {
        prefix if isinstance(prefix, six.string_types) else prefix.__name__
        for prefix in packages_to_raise
    }

    def try_import(module_name, *args, **kwargs):
        try:
            return BUILTIN_IMPORT(module_name, *args, **kwargs)
        except:
            if any((module_name.startswith(prefix) for prefix in packages_to_raise)):
                # This is a module we need to import, so we don't mock it
                # and raising the exception
                raise
            # Mock external module so we can peacefully create our client
            sys.modules[module_name] = mock.MagicMock()
            return sys.modules[module_name]

    return mock.patch('__builtin__.__import__', try_import)
