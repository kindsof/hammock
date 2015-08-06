import hammock
import hammock.resource as resource
import hammock.route as route
import jinja2
import re
import inspect


FILE_TEMPLATE = jinja2.Template("""
import requests
import logging
import bunch


def url_join(*args):
    return '/'.join(arg.strip('/') for arg in args)


class {{ class_name }}(object):

    def __init__(self, hostname, port, token=None, timeout=None):
        self._url = "http://%s:%d" % (hostname, port)
        self._client = requests.Session()
        self._timeout = timeout
        self.set_token(token)
{% for resource_name, resource_path in resources_names %}\
        self.{{ resource_name }} = self.{{ resource_name|capitalize }}(self, '{{ resource_path }}')
{% endfor %}\

    def close(self):
        self._client.close()

    def fetch(self, method, url, json=None, stream=None, success_code=200, response_type='{{ type_json }}', kwargs=None):
        url = url_join(self._url, url)
        json.update(kwargs or {})
        _kwargs = {
            "timeout": self._timeout,
            "stream": True,
        }
        if method in {"POST", "PUT"}:
            if stream:
                _kwargs["data"] = stream
                if json:
                    _kwargs["params"] = json
            else:
                if json:
                    _kwargs["json"] = json
        else:
            _kwargs["params"] = json
        logging.debug("Sending %s request: %s %s", method, url, json)
        response = getattr(self._client, method.lower())(url, **_kwargs)  # pylint: disable=star-args
        result = None
        if response_type == '{{ type_json }}':
            result = self.jsonify(response)
            logging.debug("Got response status %s, body: %s", response.status_code, result)
        elif response_type == '{{ type_octet_stream }}':
            result = response.raw
        if response.status_code != success_code:
            logging.warn(
                "Response status %d does not match expected success status %d",
                response.status_code, success_code
            )
            response.raise_for_status()
        return result

    def set_token(self, token):
        if token:
            self._client.headers.update({"{{ token_entry }}": token})
        elif "{{ token_entry }}" in self._client.headers:
            del self._client.headers["{{ token_entry }}"]

    @property
    def token(self):
        return self._client.headers.get("{{ token_entry }}")

    def jsonify(self, response):
        try:
            result = response.json()
            if type(result) == dict:
                result = bunch.Bunch(result)
            elif type(result) == list:
                result = [item if type(item) != dict else bunch.Bunch(item) for item in result]
            return result
        except ValueError:
            if response.text:
                logging.warn("Could not parse json from '%s'", response.text)
{{ resource_classes|join("") }}
""")


METHOD_TEMPLATE = jinja2.Template("""
def {{ method_name }}({{ args|join(', ') }}\
{% if kwargs %}\
{% for k, v in kwargs.iteritems() %}\
, {{ k }}={{ v }}\
{% endfor %}\
{% endif %}\
{% if keywords %}\
, **{{ keywords }}\
{% endif %}\
):
    return self._client.fetch(
        method='{{ method }}',
        url=\
{% if url %}\
url_join(\
{% endif %}\
self._url\
{% if url %}\
, '{{ url }}'\
{% if url_kw %}\
.format(\
{% for name in url_kw %}\
{{ name }}={{ name }}, \
{% endfor %}\
)\
{% endif %}\
)\
{% endif %}\
,
        json=\
{% if kw_list not in args %}\
dict(\
{% for p in params_kw %}\
{{ p }}={{ p }}, \
{% endfor %}\
{% for k, v in defaults.iteritems() %}\
{{ k }}={{ v }}, \
{% endfor %}\
{% for k in kwargs %}\
{{ k }}={{ k }}, \
{% endfor %}\
),
{% else %}\
{{ kw_list }},
{% endif %}\
{% if keywords %}\
        kwargs={{ keywords }},
{% endif %}\
{% if kw_file in args  %}\
        stream={{ kw_file }},
{% endif %}\
        response_type='{{ response_type }}',
        success_code={{ success_code }},
    )
""")


RESOURCE_CLASS_TEMPLATE = jinja2.Template("""
class {% if name %}{{ name|capitalize }}{% else %}Empty{% endif %}(object):

    def __init__(self, client, url):
        self._client = client
        self._url = url
{% for resource, resource_path in sub_resources %}\
        self.{% if resource %}{{ resource }}{% else %}empty{% endif %} = \
self.{% if resource %}{{ resource|capitalize }}{% else %}Empty{% endif %}(\
self._client, "%s/{{ resource_path }}" % self._url)
{% endfor %}\
{% for method in methods %}\
{{ method|indent(4, true) }}
{% endfor %}\
{{ sub_classes }}
""")


AUTH_METHODS_CODE = """
def login(self, username, password, tenant):
    token = self._login(username, password, tenant)
    self._client.set_token(token.token)
    return token

def logout(self, token=None):
    result = self._logout(token)
    if not token:
        self._client.set_token(None)
    return result

def refresh(self, token=None):
    new_token = self._refresh(token)
    if not token:
        self._client.set_token(new_token.token)
    return new_token
"""


class ClientGenerator(object):
    def __init__(self, class_name, resources_package):
        self._resources = {}
        hammock.iter_modules(resources_package, self._add_resource)
        resource_classes = [
            _tabify(_resource_class_code(_resource))
            for _resource in self._resources.get("", [])
        ]
        resources_names = [(r.name().translate(None, "{}./-"), r.name()) for r in self._resources.get("", [])]
        for name, resource_hirarchy in self._resources.iteritems():
            if name == "":
                continue
            resource_classes.append(_tabify(_recursion_code(name, resource_hirarchy)))
            resources_names.append((name.translate(None, "{}./-"), name))

        code = FILE_TEMPLATE.render(
            class_name=class_name,
            resources_names=resources_names,
            resource_classes=resource_classes,
            token_entry=resource.TOKEN_ENTRY,
            type_json=route.TYPE_JSON,
            type_octet_stream=route.TYPE_OCTET_STREAM,
        )
        self.code = re.sub("[ ]+\n", "\n", code).rstrip("\n")

    def _add_resource(self, package, module_name, parents):
        resource_classes = hammock.resource_classes(package, module_name)
        cur = self._resources
        for p in parents:
            cur = cur.setdefault(p, {})
        for resource_class in resource_classes:
            cur.setdefault("", []).append(resource_class)


def _resource_class_code(_resource):
    methods = [
        _method_code(**kwargs)  # pylint: disable=star-args
        for kwargs in client_methods_propeties(_resource)
    ]
    if _resource.name() == "auth":
        methods.insert(0, AUTH_METHODS_CODE)
    return RESOURCE_CLASS_TEMPLATE.render(
        name=_resource.name().translate(None, "{}/.-"), resource=_resource, methods=methods)


def _recursion_code(name, resource_hirarchy):
    sub_classes = [
        _resource_class_code(_resource)
        for _resource in resource_hirarchy.get("", [])
    ]
    sub_resources = [(_resource.name().translate(None, "{}/.-"), _resource.name()) for _resource in resource_hirarchy.get("", [])]
    for key, value in resource_hirarchy.iteritems():
        if key == "":
            continue
        sub_classes.append(_recursion_code(key, value))
        sub_resources.append((key.translate(None, "{}/.-"), key))
    return RESOURCE_CLASS_TEMPLATE.render(
        name=name.translate(None, "{}/.-"),
        sub_resources=sub_resources,
        sub_classes=_tabify("".join(sub_classes))
    )


def _tabify(text):
    return "\n".join([
        line if line == "" else "    %s" % line
        for line in text.split("\n")
    ])


def _method_code(method_name, method, url, args, kwargs, url_kw, defaults, success_code, response_type, keywords):
    params_kw = set(args) - (set(defaults) | set(url_kw) | {"self"}) - {route.KW_HEADERS, route.KW_FILE, route.KW_LIST}
    url_kw = set(url_kw) - {route.KW_HEADERS, route.KW_FILE, route.KW_LIST}
    defaults = {k: v if type(v) is not str else "'%s'" % v for k, v in defaults.items()}
    args = [arg for arg in args if arg != route.KW_HEADERS]
    assert not ((route.KW_FILE in args) and (route.KW_LIST in args)), \
        "Can only have {} or {} in method args".format(route.KW_FILE, route.KW_LIST)
    if method_name in ("login", "logout", "refresh",):
        method_name = "_%s" % method_name
    return METHOD_TEMPLATE.render(
        method_name=method_name,
        method=method,
        url=url,
        args=args,
        kwargs=kwargs,
        url_kw=url_kw,
        params_kw=params_kw,
        defaults=defaults,
        success_code=success_code,
        response_type=response_type,
        kw_file=route.KW_FILE,
        kw_list=route.KW_LIST,
        keywords=keywords,
    )


def client_methods_propeties(resource_object):
    kwargs = []
    for method in route.iter_route_methods(resource_object):
        derivative_methods = method.client_methods or {method.__name__: None}
        for method_name, method_defaults in derivative_methods.iteritems():
            method_defaults = method_defaults or {}
            spec = inspect.getargspec(method)
            method_kwargs = dict(zip(
                spec.args[len(spec.args) - len(spec.defaults):],
                spec.defaults
            )) if spec.defaults else {}
            kwargs.append(dict(
                method_name=method_name,
                method=method.method,
                url=method.path,
                args=[arg for arg in spec.args
                      if arg not in (set(method_defaults) | set(method_kwargs))],
                kwargs=method_kwargs,
                url_kw=[arg for arg in spec.args if "{{{}}}".format(arg) in method.path],
                defaults=method_defaults,
                success_code=method.success_code,
                response_type=method.response_content_type,
                keywords=spec.keywords,
            ))
    return kwargs
