from __future__ import absolute_import
from __future__ import print_function
import importlib
import inspect
import jinja2
import re
import six
import hammock.common as common
import hammock.packages as packages
import hammock
import hammock.types.file as file_module
import hammock.wrappers as wrappers

ENV = jinja2.Environment(loader=jinja2.PackageLoader('hammock.templates', 'client'))
FILE_TEMPLATE = ENV.get_template('file.j2')
METHOD_TEMPLATE = ENV.get_template('method.j2')
RESOURCE_CLASS_TEMPLATE = ENV.get_template('resource_class.j2')
AUTH_METHODS_CODE = ENV.get_template('auth_methods.j2')
IGNORE_KW = {common.KW_HEADERS, common.KW_FILE, common.KW_LIST, common.KW_CREDENTIALS, common.KW_ENFORCER}


class ClientGenerator(object):
    def __init__(self, class_name, resources_package):
        self._resources = {}

        self._add_resources(resources_package)
        resource_classes = [
            _tabify(_resource_class_code(_resource))
            for _resource in self._resources.get("", [])
        ]
        resources_names = [_resource_tuple(r) for r in self._resources.get("", [])]
        for package, resource_hirarchy in six.iteritems(self._resources):
            if package == "":
                continue
            resource_classes.append(_tabify(_recursion_code(package, resource_hirarchy)))
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
        )
        self.code = re.sub("[ ]+\n", "\n", code).rstrip("\n")

    def _add_resources(self, package):
        for resource_class, parents in packages.iter_resource_classes(package):
            cur = self._resources
            for parent in parents:
                cur = cur.setdefault(parent, {})
            cur.setdefault("", []).append(resource_class)


def _resource_class_code(_resource):
    methods = [
        _method_code(**kwargs)
        for kwargs in client_methods_propeties(_resource)
    ]
    if _resource.name() == "auth":
        methods.insert(0, AUTH_METHODS_CODE.render())  # pylint: disable=no-member
    return RESOURCE_CLASS_TEMPLATE.render(  # pylint: disable=no-member
        name=common.to_class_name(_resource.name()),
        resource=_resource,
        methods=methods,
        cli_command_name=_format_cli_command_name(_resource.cli_command_name()),
    )


def _recursion_code(package, resource_hirarchy):
    sub_classes = [
        _resource_class_code(_resource)
        for _resource in resource_hirarchy.get("", [])
    ]
    sub_resources = [_resource_tuple(_resource) for _resource in resource_hirarchy.get("", [])]
    for sub_package, value in six.iteritems(resource_hirarchy):
        if sub_package == "":
            continue
        sub_classes.append(_recursion_code(sub_package, value))
        sub_resources.append(_package_tuple(sub_package))
    return RESOURCE_CLASS_TEMPLATE.render(  # pylint: disable=no-member
        name=package.class_name,
        sub_resources=sub_resources,
        sub_classes=_tabify("".join(sub_classes)),
        cli_command_name=_format_cli_command_name(package.cli_command_name),
    )


def _format_cli_command_name(name):
    return '"{}"'.format(name) if name else name


def _resource_tuple(resource_class):
    """
    :return: a tuple of <variable_name>, <class_name>, <path>
    """
    return resource_class.client_variable_name(), resource_class.client_class_name(), resource_class.path()


def _package_tuple(package):
    """
    :return: a tuple of <variable_name>, <class_name>, <path>
    """
    return common.to_variable_name(package.class_name), package.class_name, package.path


def _tabify(text):
    return "\n".join([
        line if line == "" else "    %s" % line
        for line in text.split("\n")
    ])


def _method_code(method_name, method, url, args, kwargs, url_kw, defaults, success_code, response_type, keywords, doc_string, keyword_map):
    params_kw = set(args) - (set(defaults) | set(url_kw) | {"self"}) - IGNORE_KW
    url_kw = set(url_kw) - IGNORE_KW

    defaults = {k: v if type(v) is not str else "'%s'" % v for k, v in defaults.items()}
    args = [arg for arg in args if arg not in {common.KW_HEADERS, common.KW_CREDENTIALS, common.KW_ENFORCER}]
    assert not ((common.KW_FILE in args) and (common.KW_LIST in args)), \
        "Can only have {} or {} in method args".format(common.KW_FILE, common.KW_LIST)
    if method_name in ("login", "logout", "refresh",):
        method_name = "_%s" % method_name

    if doc_string is not None:
        # Fix doc string indentation.
        doc_string = '\n    '.join(doc_string.split('\n'))

    return METHOD_TEMPLATE.render(  # pylint: disable=no-member
        method_name=common.to_variable_name(method_name),
        method=method,
        url=url,
        args=args,
        kwargs={k: (v if not isinstance(v, six.string_types) else '"{}"'.format(v)) for k, v in six.iteritems(kwargs)},
        url_kw=url_kw,
        params_kw=params_kw,
        defaults=defaults,
        success_code=success_code,
        response_type=response_type,
        kw_file=common.KW_FILE,
        kw_list=common.KW_LIST,
        keywords=keywords,
        doc_string=doc_string,
        keyword_map=keyword_map,
    )


def client_methods_propeties(resource_object):
    kwargs = []
    for method in resource_object.iter_route_methods(wrappers.Route):
        derivative_methods = method.client_methods or {method.__name__: None}
        for method_name, method_defaults in six.iteritems(derivative_methods):
            method_defaults = method_defaults or {}
            kwargs.append(dict(
                method_name=method_name,
                method=method.method,
                url=method.path,
                args=[arg for arg in method.spec.args if arg not in method_defaults],
                kwargs=method.spec.kwargs,
                url_kw=[arg for arg in method.spec.args if "{{{}}}".format(arg) in method.path],
                defaults=method_defaults,
                success_code=method.success_code,
                response_type=method.response_content_type,
                keywords=method.spec.keywords,
                doc_string=inspect.getdoc(method),
                keyword_map=method.keyword_map,
            ))
    return kwargs


def main(class_name, package_name):
    print(ClientGenerator(class_name, importlib.import_module(package_name)).code)


if __name__ == '__main__':
    import sys
    main(*sys.argv[1:])
