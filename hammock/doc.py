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


def generate(package):
    doc = []
    for resource_class, parents in packages.iter_resource_classes(package):
        resource_path = common.url_join(*([parent.path for parent in parents] + [resource_class.path()]))
        for route in resource_class.iter_route_methods():
            arguments = []
            for name, arg in six.iteritems(route.spec.args_info):
                argument = {
                    'name': name,
                    'type': arg.type_name,
                    'doc': arg.doc,
                }
                if not isinstance(arg, _args.PositionalArg):
                    argument['default'] = arg.default,
                arguments.append(argument)

            doc.append({
                'name': route.__name__,
                'arguments': arguments,
                'method': route.method,
                'path': common.url_join(resource_path, route.path),
                'success_status': route.success_code,
                'doc': route.spec.doc,
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


if __name__ == '__main__':
    main()
