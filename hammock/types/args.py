from __future__ import absolute_import


class Arg(object):
    """Represent a function argument"""

    PARSER_TYPE_MAP = {dict: str, list: str}
    PARSER_NARGS_MAP = {dict: '*', list: '*'}
    ALLOWED_ARG_TYPES = {
        'bool': bool,
        'int': int,
        'float': float,
        'str': str,
        'list': list,
        'dict': dict,
        None: None,
    }

    def __init__(self, name, type, doc, default=None):  # pylint: disable=redefined-builtin
        self.name = name
        self.type = self._get_type(type)
        self.doc = doc
        self.default = default

    def add_to_parser(self, parser):
        parser.add_argument(self._parser_name, type=self._parser_type, default=self._parser_default, help=self.doc)

    def _get_type(self, type_string):
        if type_string and type_string not in self.ALLOWED_ARG_TYPES:
            raise RuntimeError('param type {} not allowed'.format(type_string))
        return self.ALLOWED_ARG_TYPES[type_string]

    @property
    def _parser_type(self):
        return self.PARSER_TYPE_MAP.get(self.type, self.type)

    @property
    def _parser_nargs(self):
        return self.PARSER_NARGS_MAP.get(self.type, None)

    @property
    def _parser_name(self):
        return self.name

    @property
    def _parser_default(self):
        return self.default


class DefaultArg(Arg):
    """Represent a function argument with default value"""

    @property
    def _parser_name(self):
        return '--{}'.format(self.name)


class KeywordsArg(Arg):
    """Represent a function keywords argument"""

    def __init__(self, name, doc=None):
        doc = doc or 'Extra arguments, a comma separated key=value literals.'
        super(KeywordsArg, self).__init__(name, 'dict', doc)

    @property
    def _parser_name(self):
        return '--extras',


class ReturnArg(Arg):

    def __init__(self, type, doc):  # pylint: disable=redefined-builtin
        super(ReturnArg, self).__init__(None, type, doc)
