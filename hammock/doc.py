from __future__ import absolute_import
from __future__ import print_function
import six
import argparse
import json
import yaml
import sys

import hammock.packages as packages
import hammock.common as common
import hammock.types.args as _args
import hammock.names as names
import hammock.mock_import as mock_import


def generate(package):
    doc = []
    with mock_import.mock_import([package]):
        for resource_class, parents in packages.iter_resource_classes(package):
            resource_path = common.url_join(
                *([parent.path for parent in parents] + [resource_class.path()]))
            for route in resource_class.iter_route_methods():
                arguments = []
                for name, arg in six.iteritems(route.spec.args_info):
                    argument = {
                        'name': route.keyword_map.get(name, name),
                        'type': arg.type_name,
                        'doc': arg.doc,
                    }
                    if isinstance(arg, (_args.KeywordArg, _args.OptionalArg)):
                        argument['default'] = arg.default
                    arguments.append(argument)

                doc.append({
                    'name': route.__name__,
                    'arguments': arguments,
                    'method': route.method,
                    'path': common.url_join(resource_path, route.path),
                    'success_status': route.success_code,
                    'doc': route.spec.doc,
                    'cli_command': _build_cli_command(parents, resource_class, route)
                })
    return doc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('package')
    formatter = parser.add_mutually_exclusive_group()
    formatter.add_argument('--json', action='store_true')
    formatter.add_argument('--yaml', action='store_true')
    args = parser.parse_args()
    doc = generate(args.package)
    if args.json:
        json.dump(doc, fp=sys.stdout, indent=2)
    elif args.yaml:
        yaml.dump(doc, stream=sys.stdout, default_flow_style=False)
    else:
        print(doc)


def _build_cli_command(parents, resource_class, route_method):
    if (
        route_method is False or
        resource_class.cli_command_name() is False or
        any((parent.cli_command_name is False for parent in parents))
    ):
        return None
    command = [parent.cli_command_name for parent in parents] + [
        resource_class.cli_command_name(),
        route_method.cli_command_name or names.to_command(route_method.__name__),
    ]
    return ' '.join(command)


if __name__ == '__main__':
    main()
