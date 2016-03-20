from __future__ import absolute_import
import argparse
import cliff.command as command
import cliff.show as show
import cliff.lister as lister
import hammock.types.func_spec as func_spec


def factory(func):

    spec = func_spec.FuncSpec(func)

    if spec.returns:
        if spec.returns.type is dict:
            return type(func.__name__, (CommandItem, ), {'func': func})
        elif spec.returns.type is list:
            return type(func.__name__, (CommandList, ), {'func': func})
    return type(func.__name__, (Command, ), {'func': func})


class Command(command.Command):

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


class CommandItem(Command, show.ShowOne):

    def take_action(self, parsed_args):  # pylint: disable=unused-argument
        result = self._action(parsed_args)
        names = result.keys()
        return names, (result[name] for name in names)


class CommandList(Command, lister.Lister):

    def take_action(self, parsed_args):  # pylint: disable=unused-argument
        list_result = self._action(parsed_args)
        # We expect the method to return a list of dicts, or a list of values.
        names = set()
        for one in list_result:
            # In case The user returns a simple list:
            if not isinstance(one, dict):
                return ('value', ), [(value, ) for value in list_result]
            names = names | set(one)
        return names, [
            [one.get(name) for name in names]
            for one in list_result
        ]
