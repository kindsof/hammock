from __future__ import absolute_import
import six
import logging
import requests
import argparse
import sys
import shutil
import cliff.command as command
import cliff.show as show
import cliff.lister as lister
import hammock.types.func_spec as func_spec
import hammock.cli


LOG = logging.getLogger(__name__)


def factory(func, column_order=None, column_colors=None):

    spec = func_spec.FuncSpec(func)

    overrides = {
        'func': func,
        'column_order': column_order or [],
        'column_colors': column_colors or {},
    }

    if spec.returns:
        if spec.returns.type_name == 'dict':
            return type(func.__name__, (CommandItem, ), overrides)
        elif spec.returns.type_name == 'list':
            return type(func.__name__, (CommandList, ), overrides)
        elif spec.returns.type_name == 'file':
            return type(func.__name__, (CommandFile, ), overrides)
    return type(func.__name__, (Command, ), overrides)


class Command(command.Command):

    # Lowercase names of columns, define the order in the output.
    column_order = []
    # COLORS: A dict, {column-name: {value: method-that-accepts-string-and-return-string}}
    column_colors = {}

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.spec = func_spec.FuncSpec(self.func)
        self.__doc__ = self._get_doc()

    def take_action(self, parsed_args):
        result = self._action(parsed_args)
        if result is not None and (self.spec.returns is None or self.spec.returns.type_name != 'None'):
            if self.spec.returns:
                result = self.spec.returns.convert(result)
            self.app.stdout.write(str(result) + '\n')

    def get_parser(self, prog_name):
        parser = super(Command, self).get_parser(prog_name)
        parser.formatter_class = argparse.RawTextHelpFormatter
        parser.usage = self.__doc__
        for arg in six.itervalues(self.spec.args_info):
            arg.add_to_parser(parser)
        return parser

    def _action(self, parsed_args):
        kwargs = {arg: getattr(parsed_args, arg) for arg in self.spec.all_args}
        if self.spec.keywords:
            kwargs.update(getattr(parsed_args, self.spec.keywords, ''))
        try:
            return self.func(**kwargs)
        except requests.HTTPError as exc:
            raise hammock.cli.CLIException(self._format_exception(exc))

    def _get_doc(self):
        doc = self.spec.doc or ''
        return_doc = ''
        if self.spec.returns and self.spec.returns.convert is not None:
            return_type = ' {}'.format(self.spec.returns.type_name) if self.spec.returns.type_name else ''
            return_doc = ': {}'.format(self.spec.returns.doc) if self.spec.returns.doc else ''
            return_doc = 'Returns{}{}'.format(return_type, return_doc)
        return '\n\n'.join([doc, return_doc])

    def _sorted_columns(self, columns):
        return sorted(columns, key=self._compare_columns)

    def _compare_columns(self, name):
        try:
            return self.column_order.index(name.lower())
        except ValueError:
            return len(self.column_order) + 1

    def _colorize(self, column, value):
        try:
            return self.column_colors[column][value.lower()](value)
        except KeyError:
            return value

    @staticmethod
    def _format_exception(exc):
        if 'application/json' in exc.response.headers.get('content-type', ''):
            try:
                error_content = exc.response.json()
                title = error_content.get('title')
                description = error_content.get('description')
                if title or description:
                    return description if description else title
            except:
                pass
        return 'HTTP {}\n{}'.format(exc.response.status_code, exc.response.text)


class CommandItem(Command, show.ShowOne):
    """
    Command that returns a single item,
    in the form of a dict.
    """

    def take_action(self, parsed_args):  # pylint: disable=unused-argument
        result = self._action(parsed_args)
        names = self._sorted_columns(result.keys())
        return names, (self._colorize(name, result[name]) for name in names)


class CommandList(Command, lister.Lister):
    """
    Command that returns a list of items,
    each one is a dict.
    """

    def take_action(self, parsed_args):  # pylint: disable=unused-argument
        objects = self._action(parsed_args)
        # We expect the method to return a list of dicts, or a list of values.
        names = self._get_names(objects)
        if not names:
            return ('value', ), [(value, ) for value in objects]
        return names, [
            [self._colorize(name, obj.get(name)) for name in names]
            for obj in objects
        ]

    def _get_names(self, objects):
        if not all((isinstance(obj, dict) for obj in objects)):
            return None
        keys = set()
        for obj in objects:
            keys |= set(obj)

        return self._sorted_columns(keys)


class CommandFile(Command):
    """
    Command that returns a file,
    save it into a local file.
    """

    def get_parser(self, prog_name):
        parser = super(CommandFile, self).get_parser(prog_name)
        parser.add_argument('--path', help='Destination path.')
        return parser

    def take_action(self, parsed_args):  # pylint: disable=unused-argument
        result = self._action(parsed_args)
        if parsed_args.path:
            with open(parsed_args.path, 'w') as destination:
                shutil.copyfileobj(result, destination)
        else:
            shutil.copyfileobj(result, sys.stdout)
