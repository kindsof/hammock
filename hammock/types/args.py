from __future__ import absolute_import

try:
    import ujson as json
except ImportError:
    import json
import hammock.names as names
import hammock.common as common


class PositionalArg(object):
    """Represent a function argument"""

    PARSER_TYPE_MAP = {dict: str, list: str}
    PARSER_NARGS_MAP = {dict: '*', list: '*'}
    ALLOWED_ARG_TYPES = {
        'bool': common.parse_bool,
        'int': int,
        'float': float,
        'str': str,
        'list': list,
        'dict': json.loads,
        'None': None,
        None: lambda x: x,
    }
    ALLOWED_RETURN_TYPES = {
        'bool': bool,
        'int': int,
        'float': float,
        'str': str,
        'list': list,
        'dict': dict,
        'None': None,
        'file': 'file',
        None: lambda x: x,
    }

    def __init__(self, name, type, doc, default=None):  # pylint: disable=redefined-builtin
        self.name = name
        self.type = self._get_type(type)
        self.doc = doc
        self.default = default

    def add_to_parser(self, parser):
        kwargs = {'type': self._parser_type, 'help': self.doc}
        self._parser_update_kwargs(kwargs)
        parser.add_argument(self._parser_name, **kwargs)

    def _get_type(self, type_string):
        if type_string and type_string not in self.ALLOWED_ARG_TYPES:
            raise RuntimeError('param type {} not allowed'.format(type_string))
        return self.ALLOWED_ARG_TYPES[type_string]

    @property
    def _parser_type(self):
        return self.PARSER_TYPE_MAP.get(self.type, self.type)

    @property
    def _parser_name(self):
        # Can't convert name with names.to_command, no option to add a 'dest' keyword
        # when using a positional argument.
        return self.name

    def _parser_update_kwargs(self, kwargs):
        if self.type is list:
            kwargs['nargs'] = '*'


class OptionalArg(PositionalArg):
    """Represent a function argument with default value"""

    @property
    def _parser_name(self):
        return '--{}'.format(names.to_command(self.name))

    def _parser_update_kwargs(self, kwargs):
        super(OptionalArg, self)._parser_update_kwargs(kwargs)
        # dest keyword can be added only if the argument is optional,
        kwargs['dest'] = self.name
        if self.default is True:
            kwargs['action'] = 'store_false'
            kwargs.pop('type', None)
        elif self.default is False:
            kwargs['action'] = 'store_true'
            kwargs.pop('type', None)
        else:
            kwargs['default'] = self.default


class KeywordArg(PositionalArg):
    """Represent a function keywords argument"""

    def __init__(self, name, doc=None):
        doc = doc or 'Extra arguments, a dict as a json string.'
        super(KeywordArg, self).__init__(name, 'dict', doc)

    @property
    def _parser_name(self):
        return '--{}'.format(self.name)


class ReturnArg(PositionalArg):

    def __init__(self, type, doc):  # pylint: disable=redefined-builtin
        super(ReturnArg, self).__init__(None, type, doc)

    def _get_type(self, type_string):
        if type_string and type_string not in self.ALLOWED_RETURN_TYPES:
            raise RuntimeError('return type {} not allowed'.format(type_string))
        return self.ALLOWED_RETURN_TYPES[type_string]
