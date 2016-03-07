from __future__ import absolute_import
import collections
import functools
import hammock.exceptions as exceptions
import hammock.common as common
import hammock.wrappers as wrappers
import hammock.wrappers.route as route
import hammock.wrappers.sink as sink
import warnings


class Resource(object):

    # POLICY_GROUP_NAME:
    # define a policy group wich is the prefix for the rule name,
    # together with the route's rule_name attribute the whole rule will be 'group:rule_name'
    #   if False, policy check will be disabled for the entire resource.
    #   if None, the group name is set to the class name, lowercase.
    POLICY_GROUP_NAME = None

    # CLI_COMMAND_NAME:
    # change the cli command name,
    #   if False, the Resource won't be added to the CLI.
    #   if None, the class name will be converted to a command name,
    #   otherwise, the value will be the command name.
    CLI_COMMAND_NAME = None

    def __init__(self, api, base_path=None, **resource_params):  # XXX: remove once sagittarius is fixed  # noqa  # pylint: disable=unused-argument
        self.api = api
        self._default_exception_handler = getattr(self, "DEFAULT_EXCEPTION_HANDLER", None)

    @classmethod
    def name(cls):
        return getattr(cls, "PATH", cls.__name__)

    @classmethod
    def path(cls):
        return getattr(cls, "PATH", common.to_path(cls.__name__))

    def handle_exception(self, exc, exception_handler):
        if exception_handler:
            exc = exception_handler(exc)
        elif self._default_exception_handler:
            exc = self._default_exception_handler(exc)
        raise self._to_internal_server_error(exc)

    @property
    def routes(self):
        """
        :return: A dict representing routes in a resource: { url: {method: responder} }
        """
        routes = collections.defaultdict(dict)
        for route_method in self.iter_route_methods():
            route_method.set_resource(self)
            method = route_method.method.upper()
            routes[common.url_join(self.path(), route_method.path)][method] = route_method.call
        return routes

    @property
    def sinks(self):
        """
        :return: A list representing sinks in a resource: ( url, responder )
            The list is sorted by url size, largest first.
        """
        sinks = []
        for sink_method in self.iter_sink_methods():
            sink_method.set_resource(self)
            sinks.append((common.url_join(self.path(), sink_method.path), sink_method.call))
        return sinks

    @staticmethod
    def _to_internal_server_error(exc):
        return exc if isinstance(exc, exceptions.HttpError) else exceptions.InternalServerError(str(exc))

    @classmethod
    def iter_route_methods(cls, reoute_class=route.Route):
        return (
            getattr(cls, attr) for attr in dir(cls)
            if isinstance(getattr(cls, attr, None), reoute_class)
        )

    @classmethod
    def iter_sink_methods(cls):
        return sorted(
            (
                getattr(cls, attr) for attr in dir(cls)
                if isinstance(getattr(cls, attr, None), sink.Sink)
            ),
            key=functools.cmp_to_key(lambda p1, p2: len(p1.path) - len(p2.path))
        )

    @classmethod
    def client_variable_name(cls):
        return common.to_variable_name(cls.name())

    @classmethod
    def client_class_name(cls):
        return common.to_class_name(cls.name())

    @classmethod
    def cli_command_name(cls):
        if cls.CLI_COMMAND_NAME or cls.CLI_COMMAND_NAME is False:
            return cls.CLI_COMMAND_NAME
        return common.to_path(cls.name())


# XXX: deprecated, those methods will be removed

def get(path='', **kwargs):
    warnings.warn('resource.get is deprecated, use hammock.get instead', UserWarning)
    return wrappers.wrapper(path, 'GET', **kwargs)


def head(path='', **kwargs):
    warnings.warn('resource.head is deprecated, use hammock.head instead', UserWarning)
    return wrappers.wrapper(path, 'HEAD', **kwargs)


def post(path='', **kwargs):
    warnings.warn('resource.post is deprecated, use hammock.post instead', UserWarning)
    return wrappers.wrapper(path, 'POST', **kwargs)


def put(path='', **kwargs):
    warnings.warn('resource.put is deprecated, use hammock.put instead', UserWarning)
    return wrappers.wrapper(path, 'PUT', **kwargs)


def delete(path='', **kwargs):
    warnings.warn('resource.delete is deprecated, use hammock.delete instead', UserWarning)
    return wrappers.wrapper(path, 'DELETE', **kwargs)
