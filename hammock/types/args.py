from __future__ import absolute_import

import hammock.names as names
import hammock.converters as converters


class PositionalArg(object):
    """Represent a function argument"""

    PARSER_TYPE_MAP = {dict: str, list: str}
    ALLOWED_ARG_TYPES = {
        'bool': converters.to_bool,
        'bool[True]': converters.to_bool,
        'bool[False]': converters.to_bool,
        'int': converters.to_int,
        'float': converters.to_float,
        'str': converters.to_str,
        'list': converters.to_list,
        'dict': converters.to_dict,
        'None': converters.to_none,
        None: lambda x: x,
    }
    ALLOWED_RETURN_TYPES = {
        'bool': converters.to_bool,
        'int': converters.to_int,
        'float': converters.to_float,
        'str': converters.to_str,
        'list': converters.to_list,
        'dict': converters.to_dict,
        'None': converters.to_none,
        'file': 'file',
        None: lambda x: x,
    }

    def __init__(self, name, type, doc, default=None):  # pylint: disable=redefined-builtin
        self.name = name
        self.type_name = type
        self.convert = self._get_converter()
        self.doc = doc
        self.default = default

    def add_to_parser(self, parser):
        kwargs = {'type': self._parser_type, 'help': self.doc}
        self._parser_update_kwargs(kwargs)
        parser.add_argument(self._parser_name, **kwargs)

    def _get_converter(self):
        if self.type_name and self.type_name not in self.ALLOWED_ARG_TYPES:
            raise RuntimeError('param type {} not allowed'.format(self.type_name))
        return self.ALLOWED_ARG_TYPES[self.type_name]

    @property
    def _parser_type(self):
        return self.PARSER_TYPE_MAP.get(self.convert, self.convert)

    @property
    def _parser_name(self):
        return self.name

    def _parser_update_kwargs(self, kwargs):
        self._update_list_kwargs(kwargs)
        kwargs['metavar'] = self.name.strip('_')

    def _update_list_kwargs(self, kwargs):
        if self.type_name == 'list':
            kwargs['nargs'] = '+'
            kwargs.pop('type', None)
            # Always list is an optional CLI argument.
            if not self._parser_name.startswith('--'):
                self.name = '--' + self.name


class OptionalArg(PositionalArg):
    """Represent a function argument with default value"""

    @property
    def _parser_name(self):
        return '--{}'.format(names.to_command(self.name).strip('_'))

    def _parser_update_kwargs(self, kwargs):
        self._update_list_kwargs(kwargs)
        kwargs['dest'] = self.name
        if self.type_name == 'bool[True]':
            kwargs['action'] = 'store_false'
            kwargs.pop('type', None)
        elif self.type_name == 'bool[False]':
            kwargs['action'] = 'store_true'
            kwargs.pop('type', None)
        else:
            kwargs['metavar'] = self.name.strip('_').upper()

        # If a list, change nargs from '+' to '*'
        if kwargs.get('nargs') == '+':
            kwargs['nargs'] = '*'
        else:
            kwargs['default'] = self.default


class KeywordArg(PositionalArg):
    """Represent a function keywords argument"""

    def __init__(self, name, doc=None):
        doc = doc or 'Extra arguments, a dict as a json string.'
        super(KeywordArg, self).__init__(name, 'dict', doc)

    @property
    def _parser_name(self):
        return '--{}'.format(self.name.strip('_'))

    def _parser_update_kwargs(self, kwargs):
        kwargs['dest'] = self.name


class ReturnArg(PositionalArg):

    def __init__(self, type, doc):  # pylint: disable=redefined-builtin
        super(ReturnArg, self).__init__(None, type, doc)

    def _get_converter(self):
        if self.type_name and self.type_name not in self.ALLOWED_RETURN_TYPES:
            raise RuntimeError('return type {} not allowed'.format(self.type_name))
        return self.ALLOWED_RETURN_TYPES[self.type_name]
