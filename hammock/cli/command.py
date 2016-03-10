from __future__ import absolute_import
import argparse
import cliff.command as command
import cliff.show as show
import cliff.lister as lister
import hammock.types.func_spec as func_spec


def factory(func, commands):

    spec = func_spec.FuncSpec(func)

    def _action(parsed_args):
        kwargs = {
            arg: getattr(parsed_args, arg)
            for arg in (set(spec.args) | set(spec.kwargs))
        }
        return func(**kwargs)

    def action_show_one(inner_self, parsed_args):  # pylint: disable=unused-argument
        result = _action(parsed_args)
        names = result.keys()
        return names, (result[name] for name in names)

    def action_list(inner_self, parsed_args):  # pylint: disable=unused-argument
        list_result = _action(parsed_args)
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

    def action_command(inner_self, parsed_args):
        result = _action(parsed_args)
        if result is not None:
            inner_self.app.stdout.write(str(result) + '\n')

    super_class = command.Command
    take_action = action_command
    if spec.returns:
        if spec.returns.type is dict:
            super_class = show.ShowOne
            take_action = action_show_one
        elif spec.returns.type is list:
            super_class = lister.Lister
            take_action = action_list

    def get_parser(inner_self, prog_name):
        parser = super_class.get_parser(inner_self, prog_name)
        parser.formatter_class = argparse.RawTextHelpFormatter

        # add all method arguments to parser
        for name in spec.kwargs.keys() + spec.args:
            spec.args_info(name).add_to_parser(parser)
        if spec.keywords:
            spec.args_info(spec.keywords).add_to_parser(parser)
        return parser

    return type(
        _to_class_name(' '.join(commands + [func.__name__])),
        (super_class, ),
        {
            'take_action': take_action,
            'get_parser': get_parser,
            '__doc__': _get_doc(spec),
        }
    )


def _get_doc(spec):
    doc = spec.doc or ''

    return_doc = ''
    if spec.returns:
        return_type = ' {}'.format(spec.returns.type) if spec.returns.type else ''
        return_doc = ': {}'.format(spec.returns.doc) if spec.returns.doc else ''
        return_doc = 'Returns{}{}'.format(return_type, return_doc)

    return '\n\n'.join([doc, return_doc])


def _to_class_name(spaced):
    return ''.join(part.capitalize() for part in spaced.split())
