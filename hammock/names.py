from __future__ import absolute_import
import re
import functools


REMOVE_NAME_INVALID_CHARS = functools.partial(re.compile(r'[./]').sub, '')
PATH_VARIABLE = re.compile(r'{([^}]+)}')
REMOVE_VARIABLES = functools.partial(PATH_VARIABLE.sub, r'_')
CONVERT_PATH_VARIABLES = functools.partial(PATH_VARIABLE.sub, r'(?P<\1>[^/]+)')
SPLIT_CAMEL_BLOCKS = functools.partial(re.compile(r'[A-Z][a-z0-9_$]+').sub, lambda match: '_{}_'.format(match.group(0)))


def _to_parts(name):
    name = name.replace('-', '_')
    name = SPLIT_CAMEL_BLOCKS(name).strip('_').lower()
    return [part for part in name.split('_') if part]


def to_variable_name(name):
    starts_with_underscore = name.startswith('_')
    name = REMOVE_VARIABLES(name)
    name = REMOVE_NAME_INVALID_CHARS(name)
    name = '_'.join(_to_parts(name)).replace('-', '_')
    if starts_with_underscore:
        name = '_' + name
    return name


def to_class_name(name):
    name = REMOVE_VARIABLES(name)
    name = REMOVE_NAME_INVALID_CHARS(name)
    parts = [(part[0].capitalize() + part[1:] if part else '') for part in _to_parts(name)]
    return ''.join(parts).replace('-', '_')


def to_path(name):
    return '-'.join(_to_parts(name))


def to_command(name):
    name = REMOVE_VARIABLES(name)
    name = REMOVE_NAME_INVALID_CHARS(name)
    return '-'.join(_to_parts(name)).replace('_', '-')
