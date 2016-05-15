from __future__ import absolute_import
import collections
import functools
import logging
import sys
import six

import hammock.exceptions as exceptions
import hammock.common as common
import hammock.names as names
import hammock.wrappers as wrappers
import hammock.types.func_spec as func_spec
import hammock


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

    def __init__(self, **resource_params):
        self.params = resource_params
        self._specs = {}
        self._default_exception_handler = getattr(self, "DEFAULT_EXCEPTION_HANDLER", None)

    @classmethod
    def name(cls):
        return getattr(cls, "PATH", cls.__name__)

    @classmethod
    def path(cls):
        return getattr(cls, "PATH", names.to_path(cls.__name__))

    @classmethod
    def policy_group_name(cls):
        if cls.POLICY_GROUP_NAME is False:
            return False
        return cls.POLICY_GROUP_NAME or names.to_command(cls.name().lower())

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
                'Error handling exception {:r}: {}'.format(exc, str(handle_exception)))
        finally:
            # If exception was not converted yet, we convert it to internal server error.
            if not isinstance(exc, exceptions.HttpError):
                exc = exceptions.InternalServerError(repr(exc))

            # Raise exc, with the original traceback
            six.reraise(exc, None, sys.exc_info()[2])

    @property
    def routes(self):
        """
        :return: A dict representing routes in a resource: { url: {method: responder} }
        """
        routes = collections.defaultdict(dict)
        errors = []
        for route_method in self.iter_route_methods():
            try:
                route_method.set_resource(self)
                routes[common.url_join(self.path(), route_method.path)][route_method.method] = route_method.call
            except exceptions.BadResourceDefinition as exc:
                errors.append(exc)
        if errors:
            for error in errors:
                logging.error(error)
            raise exceptions.BadResourceDefinition('Bad definition of resource, see log for errors.')
        return routes

    @property
    def sinks(self):
        """
        :return: A list representing sinks in a resource: ( url, responder )
            The list is sorted by url size, largest first.
        """
        sinks = []
        errors = []
        for sink_method in self.iter_sink_methods():
            try:
                sink_method.set_resource(self)
                sinks.append((common.url_join(self.path(), sink_method.path), sink_method.call))
            except exceptions.BadResourceDefinition as exc:
                errors.append(exc)
        if errors:
            for error in errors:
                logging.error(error)
            raise exceptions.BadResourceDefinition('Bad definition of resource, see log for errors.')
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

    def check_spec_match(self, method_name, kwargs):
        if method_name not in self._specs:
            self._specs[method_name] = func_spec.FuncSpec(getattr(self, method_name))
        try:
            self._specs[method_name].match_and_convert(kwargs)
        except TypeError as exc:
            raise hammock.exceptions.BadRequest('Bad arguments: {}'.format(exc))
