from __future__ import absolute_import
import collections
import functools
import warnings
import logging
import sys
import six

import hammock.exceptions as exceptions
import hammock.common as common
import hammock.names as names
import hammock.wrappers as wrappers


LOG = logging.getLogger(__name__)


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
        return getattr(cls, "PATH", names.to_path(cls.__name__))

    def handle_exception(self, exc, exception_handler, request_uuid):
        """
        Convert the exception to HTTP error
        """
        try:
            if exception_handler:
                exc = exception_handler(exc)
            elif self._default_exception_handler:
                exc = self._default_exception_handler(exc)
            common.log_exception(exc, request_uuid)
        except Exception as handle_exception:  # pylint: disable=broad-except
            exc = exceptions.InternalServerError(
                'Error handling exception {}: {}'.format(str(exc), str(handle_exception)))
        finally:
            # If exception was not converted yet, we convert it to internal server error.
            if not isinstance(exc, exceptions.HttpError):
                exc = exceptions.InternalServerError(str(exc))

            # Raise exc, with the original traceback
            six.reraise(exc, None, sys.exc_info()[2])

    @property
    def routes(self):
        """
        :return: A dict representing routes in a resource: { url: {method: responder} }
        """
        routes = collections.defaultdict(dict)
        for route_method in self.iter_route_methods():
            route_method.set_resource(self)
            routes[common.url_join(self.path(), route_method.path)][route_method.method] = route_method.call
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

    @classmethod
    def iter_route_methods(cls, route_class=wrappers.Route):
        return (
            getattr(cls, attr) for attr in dir(cls)
            if isinstance(getattr(cls, attr, None), route_class)
        )

    @classmethod
    def iter_sink_methods(cls):
        return sorted(
            (
                getattr(cls, attr) for attr in dir(cls)
                if isinstance(getattr(cls, attr, None), wrappers.Sink)
            ),
            key=functools.cmp_to_key(lambda p1, p2: len(p1.path) - len(p2.path))
        )

    @classmethod
    def client_variable_name(cls):
        return names.to_variable_name(cls.name())

    @classmethod
    def client_class_name(cls):
        return names.to_class_name(cls.name())

    @classmethod
    def cli_command_name(cls):
        return cls.CLI_COMMAND_NAME if cls.CLI_COMMAND_NAME is not None else names.to_command(cls.name())

    @classmethod
    def route_cli_commands_map(cls):
        mapping = {}
        for route_method in cls.iter_route_methods():
            method_name = names.to_variable_name(route_method.__name__)
            command_name = route_method.cli_command_name
            if command_name is False:
                mapping[method_name] = False
            elif route_method.client_methods:
                for name in route_method.client_methods:
                    mapping[name] = names.to_command(name)
            else:
                mapping[method_name] = command_name or names.to_command(route_method.__name__)
        return mapping


# XXX: deprecated, those methods will be removed

def get(path='', **kwargs):
    warnings.warn('resource.get is deprecated, use hammock.get instead', UserWarning)
    return lambda func: wrappers.Route(func, path, 'GET', **kwargs)


def head(path='', **kwargs):
    warnings.warn('resource.head is deprecated, use hammock.head instead', UserWarning)
    return lambda func: wrappers.Route(func, path, 'HEAD', **kwargs)


def post(path='', **kwargs):
    warnings.warn('resource.post is deprecated, use hammock.post instead', UserWarning)
    return lambda func: wrappers.Route(func, path, 'POST', **kwargs)


def put(path='', **kwargs):
    warnings.warn('resource.put is deprecated, use hammock.put instead', UserWarning)
    return lambda func: wrappers.Route(func, path, 'PUT', **kwargs)


def delete(path='', **kwargs):
    warnings.warn('resource.delete is deprecated, use hammock.delete instead', UserWarning)
    return lambda func: wrappers.Route(func, path, 'DELETE', **kwargs)
