from __future__ import absolute_import
import six
import logging
import hammock.proxy as proxy
import hammock.common as common
import hammock.exceptions as exceptions
import hammock.types.response as response
from . import wrapper


class Route(wrapper.Wrapper):
    """
    Decorates a routing method
    """

    def __init__(
        self, func, path, method,
        success_code=200,
        keyword_map=None,
        rule_name=None,
        client_methods=None,
        cli_command_name=None,
        response_content_type=common.TYPE_JSON,
        **kwargs
    ):
        """
        Create a decorator of a rout method in a resource class
        :param func: a function to decorate
        :param path: url path of the function
        :param method: HTTP method
        :param success_code: a code to return in http response.
        :param keyword_map: a mapping between request keywords to required method keywords.
        :param rule_name: a rule from policy.json
        :param client_methods: a dict of how the method will look like in client code,
            and overriding keys - values for method parameters.
            { method-name: { key: value }}
        :param cli_command_name: override cli command name for a route
            if None, the command name will not be overridden.
            if False, the command will not be added to the cli.
        :param response_content_type: content type of response.
        :param kwargs: wrappers.Wrapper keyword arguments
        :return: the func, decorated
        """
        super(Route, self).__init__(func, path, **kwargs)
        self.method = method.upper()
        self.success_code = self.get_status_code(success_code)
        self.client_methods = client_methods
        self.cli_command_name = cli_command_name
        self.keyword_map = keyword_map
        self.rule_name = rule_name
        self.full_policy_rule_name = None
        self.response_content_type = response_content_type

        self._validate_keyword_map()

        if self.method in common.URL_PARAMS_METHODS and common.KW_LIST in (set(self.spec.args) | set(self.spec.kwargs)):
            raise exceptions.BadResourceDefinition(
                "Can't declare a url params method with _list argument, it it useful only when you get request body.")

    def _wrapper(self, req):
        """
        Wraps the decorated func (self._func)
        :param req: a hammock.types.request.Request object.
        :return: response as hammock.types.response.Response object.
        """
        if self.dest is None:
            kwargs = self._extract_kwargs(req, req.collected_data)
            if self.full_policy_rule_name:
                enforcer, credentials = self._resource.api.policy.check(self.full_policy_rule_name, target=kwargs, headers=req.headers)
                if common.KW_CREDENTIALS in self.spec.args:
                    kwargs[common.KW_CREDENTIALS] = credentials
                if common.KW_ENFORCER in self.spec.args:
                    kwargs[common.KW_ENFORCER] = enforcer

            # Convert arguments according to expected type
            self._convert_argument_types(kwargs)
            # Add headers:
            if common.KW_HEADERS in self.spec.args:
                kwargs[common.KW_HEADERS] = req.headers
            if common.KW_HOST in self.spec.args:
                kwargs[common.KW_HOST] = '{}://{}'.format(req.parsed_url.scheme, req.parsed_url.netloc)

            # Invoke the routing method:
            result = self(**kwargs)

            resp = response.Response.from_result(result, self.success_code, self.response_content_type)
        else:
            resp = proxy.proxy(req, self.dest)
        return resp

    def set_resource(self, resource):
        super(Route, self).set_resource(resource)
        if not self._is_policy_disabled:
            self.full_policy_rule_name = self._generate_full_policy_rule_name()
        else:
            self.full_policy_rule_name = None
            # check if a method that enforces policy, expects enforcer.
            if common.KW_ENFORCER in self.spec.args:
                raise self._error(
                    exceptions.BadResourceDefinition,
                    'Method {} in class {} has argument {}, thus should be in policy file'.format(
                        self.__name__, self._resource.__class__.__name__, common.KW_ENFORCER))

    def _extract_kwargs(self, req, collected_data):
        try:
            kwargs = self._convert_to_kwargs(req, collected_data)
            logging.debug('[kwargs %s] %s', req.uid, kwargs)
            return kwargs
        except exceptions.HttpError:
            raise
        except Exception as exc:  # pylint: disable=broad-except
            logging.exception('[Error parsing request kwargs %s] %r', req.uid, exc)
            raise exceptions.BadRequest('Error parsing request parameters, {:r}'.format(exc))

    def _convert_to_kwargs(self, req, collected_data):
        args = list(set(self.spec.args[:]) - {common.KW_CREDENTIALS, common.KW_ENFORCER, common.KW_HEADERS, common.KW_HOST})
        kwargs = collected_data

        for keyword, error_msg in (
            (common.KW_FILE, 'expected {} as {}'.format(common.CONTENT_TYPE, common.TYPE_OCTET_STREAM)),
            (common.KW_LIST, 'expected {} {} as list'.format(common.CONTENT_TYPE, common.TYPE_JSON)),
        ):
            if keyword in args:
                try:
                    kwargs[keyword] = req.collected_data[self._get_mapped_keyword(keyword)]
                except KeyError:
                    raise exceptions.BadData(error_msg)

                args.remove(keyword)

        expected = set([self._get_mapped_keyword(arg) for arg in args])
        request_arguments = set(kwargs)
        missing = expected - request_arguments
        if missing:
            raise exceptions.BadRequest(
                'Missing parameters: {}. Request arguments {}. Expected {}.'.format(
                    ', '.join(missing), ', '.join(request_arguments), ', '.join(expected)))

        # Handle args keyword conversion
        kwargs.update({keyword: kwargs.pop(self._get_mapped_keyword(keyword)) for keyword in args})

        # Handle kwargs keyword conversion
        kwargs.update({keyword: kwargs.pop(self._get_mapped_keyword(keyword), default)
                       for keyword, default in six.iteritems(self.spec.kwargs)})

        return kwargs

    def _convert_argument_types(self, data):
        """
        Inplace conversion of the data types according to self.spec
        :param data: keyword arguments supposed to be passed to self.func
        """
        for name, value in six.iteritems(data):
            arg = self.spec.args_info(name)
            if arg.convert is list:
                if not isinstance(value, list):
                    data[name] = [value] if value is not None else []
            elif arg.convert is not None and value is not None:
                try:
                    data[name] = arg.convert(value)
                except ValueError as exc:
                    raise exceptions.BadRequest(
                        "argument {} should be of type {}, got bad value: '{}'. ({})".format(
                            name, arg.type_name, value, exc))

    @staticmethod
    def get_status_code(status):
        """
        Return http status code as int, even if status is of the form "201 Created" for example.
        :param status: http status code, int or string.
        :return: code as int
        """
        if isinstance(status, int):
            return status
        else:
            return int(status.split(' ')[0])

    @property
    def _is_policy_disabled(self):
        return (self._resource.policy_group_name() is False) or (self.dest is not None) or self._resource.api.policy.is_disabled

    def _generate_full_policy_rule_name(self):
        group_name = self._resource.policy_group_name()
        rule_name = self.rule_name or self.__name__
        full_policy_rule_name = '{}:{}'.format(group_name, rule_name)
        if full_policy_rule_name not in self._resource.api.policy.rules:
            raise self._error(
                exceptions.BadResourceDefinition,
                'Policy rule {} does not exist in policy file'.format(full_policy_rule_name))
        return full_policy_rule_name

    def _get_mapped_keyword(self, original_keyword):
        """Return the alternative keyword if one exists."""
        if original_keyword not in self.keyword_map:
            return original_keyword

        return self.keyword_map[original_keyword]

    def _validate_keyword_map(self):
        """Validate the keyword map content."""
        if not self.keyword_map:
            self.keyword_map = {}
            return

        func_args = set(self.spec.args) | set(self.spec.kwargs)
        mapped_args = set(self.keyword_map.keys())
        invalid_arguments = mapped_args - func_args

        if invalid_arguments:
            raise self._error(
                exceptions.BadResourceDefinition,
                'Mapped arguments {} are not in method arguments'.format(', '.join(invalid_arguments)))

        if len(set(self.keyword_map.values())) < len(self.keyword_map):
            raise self._error(
                exceptions.BadResourceDefinition,
                'Multiple keywords are mapped to the same one {}'.format(self.keyword_map))

    def _error(self, exception_type, description):
        return exception_type('[Resource {}.{}:{}] {}'.format(
            self._resource.__class__.__module__, self._resource.__class__.__name__, self.__name__, description))
