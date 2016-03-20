from __future__ import absolute_import
import argparse
import cliff.command as command
import cliff.show as show
import cliff.lister as lister
import hammock.types.func_spec as func_spec


def factory(func, column_order=None, column_colors=None):

    spec = func_spec.FuncSpec(func)

    overrides = {
        'func': func,
        'column_order': column_order or [],
        'column_colors': column_colors or {},
    }

    if spec.returns:
        if spec.returns.type is dict:
            return type(func.__name__, (CommandItem, ), overrides)
        elif spec.returns.type is list:
            return type(func.__name__, (CommandList, ), overrides)
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
        if result is not None and (self.spec.returns is None or self.spec.returns.type is not None):
            if self.spec.returns:
                result = self.spec.returns.type(result)
            self.app.stdout.write(str(result) + '\n')

    def get_parser(self, prog_name):
        parser = super(Command, self).get_parser(prog_name)
        parser.formatter_class = argparse.RawTextHelpFormatter

        # add all method arguments to parser
        for name in self.spec.kwargs.keys() + self.spec.args:
            self.spec.args_info(name).add_to_parser(parser)
        if self.spec.keywords:
            self.spec.args_info(self.spec.keywords).add_to_parser(parser)
        return parser

    def _action(self, parsed_args):
        kwargs = {
            arg: getattr(parsed_args, arg)
            for arg in (set(self.spec.args) | set(self.spec.kwargs))
        }
        return self.func(**kwargs)

    def _get_doc(self):
        doc = self.spec.doc or ''
        return_doc = ''
        if self.spec.returns and self.spec.returns.type is not None:
            return_type = ' {}'.format(self.spec.returns.type) if self.spec.returns.type else ''
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


class CommandItem(Command, show.ShowOne):

    def take_action(self, parsed_args):  # pylint: disable=unused-argument
        result = self._action(parsed_args)
        names = self._sorted_columns(result.keys())
        return names, (self._colorize(name, result[name]) for name in names)


class CommandList(Command, lister.Lister):

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
