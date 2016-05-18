from __future__ import absolute_import
from __future__ import print_function
import importlib
import inspect
import jinja2
import re
import six

import hammock
import hammock.common as common
import hammock.names as names
import hammock.packages as packages
import hammock.types.func_spec as func_spec
import hammock.types.file as file_module
import hammock.wrappers as wrappers


ENV = jinja2.Environment(loader=jinja2.PackageLoader('hammock.templates', 'client'))
FILE_TEMPLATE = ENV.get_template('file.j2')
METHOD_TEMPLATE = ENV.get_template('method.j2')
RESOURCE_CLASS_TEMPLATE = ENV.get_template('resource_class.j2')
IGNORE_KW = {common.KW_HEADERS, common.KW_FILE, common.KW_LIST, common.KW_CREDENTIALS, common.KW_ENFORCER}


class ClientGenerator(object):
    def __init__(self, class_name, resources_package, default_url=''):
        self._resources = {}

        self._add_resources(resources_package)
        resource_classes = [
            _tabify(_resource_class_code(_resource))
            for _resource in self._resources.get("", [])
        ]
        resources_names = [_resource_tuple(r) for r in self._resources.get("", [])]
        for package, resource_hierarchy in six.iteritems(self._resources):
            if package == "":
                continue
            resource_classes.append(_tabify(_recursion_code(package, resource_hierarchy)))
            resources_names.append(_package_tuple(package))

        code = FILE_TEMPLATE.render(  # pylint: disable=no-member
            class_name=class_name,
            resources_names=resources_names,
            resource_classes=resource_classes,
            token_entry=hammock.TOKEN_ENTRY,
            type_json=common.TYPE_JSON,
            type_octet_stream=common.TYPE_OCTET_STREAM,
            url_params_methods=common.URL_PARAMS_METHODS,
            file_class=inspect.getsource(file_module.File),
            default_url=default_url,
        )
        self.code = re.sub("[ ]+\n", "\n", code).rstrip("\n")

    def _add_resources(self, package):
        for resource_class, parents in packages.iter_resource_classes(package):
            cur = self._resources
            for parent in parents:
                cur = cur.setdefault(parent, {})
            cur.setdefault("", []).append(resource_class)


def _resource_class_code(_resource, paths=None):
    paths = paths or []
    methods = []
    for kwargs in client_methods_properties(_resource, paths):
        methods.append(_method_code(**kwargs))

    return RESOURCE_CLASS_TEMPLATE.render(  # pylint: disable=no-member
        name=_resource.client_class_name(),
        resource=_resource,
        methods=methods,
        cli_command_name=_format_cli_command_name(_resource.cli_command_name()),
        route_cli_commands_map=_resource.route_cli_commands_map(),
    )


def _recursion_code(package, resource_hierarchy, paths=None):
    paths = paths or []
    sub_classes = [
        _resource_class_code(_resource, paths)
        for _resource in resource_hierarchy.get("", [])
    ]
    sub_resources = [_resource_tuple(_resource) for _resource in resource_hierarchy.get("", [])]
    for sub_package, value in six.iteritems(resource_hierarchy):
        if sub_package == "":
            continue
        sub_classes.append(_recursion_code(sub_package, value, paths + [sub_package.path]))
        sub_resources.append(_package_tuple(sub_package))
    return RESOURCE_CLASS_TEMPLATE.render(  # pylint: disable=no-member
        name=package.class_name,
        sub_resources=sub_resources,
        sub_classes=_tabify("".join(sub_classes)),
        cli_command_name=_format_cli_command_name(package.cli_command_name),
        route_cli_commands_map={},
    )


def _format_cli_command_name(name):
    return '"{}"'.format(name) if isinstance(name, six.string_types) else name


def _resource_tuple(resource_class):
    """
    :return: a tuple of <variable_name>, <class_name>, <path>
    """
    return resource_class.client_variable_name(), resource_class.client_class_name(), resource_class.path()


def _package_tuple(package):
    """
    :return: a tuple of <variable_name>, <class_name>, <path>
    """
    return names.to_variable_name(package.class_name), package.class_name, package.path


def _tabify(text):
    return "\n".join([
        line if line == "" else "    %s" % line
        for line in text.split("\n")
    ])


def _method_code(method_name, method, url, args, kwargs, url_kw, defaults, success_code, keywords, doc_string, keyword_map):
    params_kw = set(args) - (set(defaults) | set(url_kw) | {"self"}) - IGNORE_KW
    url_kw = set(url_kw) - IGNORE_KW

    defaults = {k: v if type(v) is not str else "'%s'" % v for k, v in defaults.items()}
    args = [arg for arg in args if arg not in {common.KW_HEADERS, common.KW_CREDENTIALS, common.KW_ENFORCER}]
    assert not ((common.KW_FILE in args) and (common.KW_LIST in args)), \
        "Can only have {} or {} in method args".format(common.KW_FILE, common.KW_LIST)

    if doc_string is not None:
        # Fix doc string indentation.
        doc_string = '\n    '.join(doc_string.split('\n'))

    return METHOD_TEMPLATE.render(  # pylint: disable=no-member
        method_name=names.to_variable_name(method_name),
        method=method,
        url=url,
        args=args,
        kwargs={k: (v if not isinstance(v, six.string_types) else '"{}"'.format(v)) for k, v in six.iteritems(kwargs)},
        url_kw=url_kw,
        params_kw=params_kw,
        defaults=defaults,
        success_code=success_code,
        kw_file=common.KW_FILE,
        kw_list=common.KW_LIST,
        keywords=keywords,
        doc_string=doc_string,
        keyword_map=keyword_map,
    )


def client_methods_properties(resource_object, paths):
    methods = []
    for method in resource_object.iter_route_methods(wrappers.Route):
        derivative_methods = method.client_methods or {method.__name__: None}
        for method_name, method_defaults in six.iteritems(derivative_methods):
            method_defaults = method_defaults or {}
            url = '/'.join(paths + [resource_object.path(), method.path])

            args = [arg for arg in method.spec.args if arg not in method_defaults]
            kwargs = method.spec.kwargs
            keywords = method.spec.keywords
            doc_string = inspect.getdoc(method)

            if method_defaults and hasattr(resource_object, method_name):
                sub_method = getattr(resource_object, method_name)
                doc_string = inspect.getdoc(sub_method)
                sub_spec = func_spec.FuncSpec(sub_method)
                args = sub_spec.args
                kwargs = sub_spec.kwargs
                keywords = sub_spec.keywords

            methods.append(dict(
                method_name=method_name,
                method=method.method,
                url=method.path,
                args=args,
                kwargs=kwargs,
                url_kw=[arg for arg in method.spec.args if "{{{}}}".format(arg) in url],
                defaults=method_defaults,
                success_code=method.success_code,
                keywords=keywords,
                doc_string=doc_string,
                keyword_map=method.keyword_map,
            ))
    return methods


def main(class_name, package_name, default_url=''):
    print(ClientGenerator(class_name, importlib.import_module(package_name), default_url).code)


if __name__ == '__main__':
    import sys
    main(*sys.argv[1:])
