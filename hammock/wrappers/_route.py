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
    METHOD_SPECIAL_ARGS = {common.KW_CREDENTIALS, common.KW_ENFORCER, common.KW_HEADERS, common.KW_HOST}

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

        if self.method in common.URL_PARAMS_METHODS and common.KW_LIST in self.spec.all_args:
            raise exceptions.BadResourceDefinition(
                "Can't declare a url params method with _list argument, it it useful only when you get request body.")

        self.required_args = set(self.spec.args) - self.METHOD_SPECIAL_ARGS
        self.required_args_mapped = {self._get_mapped_keyword(arg) for arg in self.required_args}

    def _wrapper(self, req):
        """
        Wraps the decorated func (self._func)
        :param req: a hammock.types.request.Request object.
        :return: response as hammock.types.response.Response object.
        """
        if self.dest is None:
            kwargs = req.collected_data
            self._convert_by_keyword_map(kwargs)
            enforcer = None
            credentials = None
            if self.credentials_class:
                credentials = self.credentials_class(req.headers)
                if self.full_policy_rule_name:
                    enforcer = self.policy.check(
                        self.full_policy_rule_name, target=kwargs, credentials=credentials)

            # Add special keyword arguments:
            if common.KW_HEADERS in self.spec.args:
                kwargs[common.KW_HEADERS] = req.headers
            if common.KW_HOST in self.spec.args:
                kwargs[common.KW_HOST] = '{}://{}'.format(req.parsed_url.scheme, req.parsed_url.netloc)
            if common.KW_CREDENTIALS in self.spec.args:
                kwargs[common.KW_CREDENTIALS] = credentials
            if common.KW_ENFORCER in self.spec.args:
                kwargs[common.KW_ENFORCER] = enforcer

            try:
                self.spec.match_and_convert(kwargs)
            except exceptions.HttpError as exc:
                raise self._error(exceptions.BadRequest, str(exc))
            except Exception as exc:  # pylint: disable=broad-except
                logging.exception('[Error parsing request kwargs %s] kwargs: %s, %r', req.uid, kwargs, exc)
                raise self._error(exceptions.BadRequest, 'Error parsing request parameters, {}'.format(exc))

            # Invoke the routing method:
            logging.debug('[kwargs %s] %s', req.uid, kwargs)
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

    def _convert_by_keyword_map(self, collected_data):
        """
        Convert from request data to method arguments, according to mapping
        """
        # Check for missing according to mapped arguments
        missing = self.required_args_mapped - set(collected_data)
        if missing:
            raise self._error(exceptions.BadRequest, 'Missing arguments: {}. Required: {}'.format(missing, self.required_args))
        # Handle args keyword conversion
        collected_data.update({
            keyword: collected_data.pop(self._get_mapped_keyword(keyword))
            for keyword in self.required_args
        })
        # Handle kwargs keyword conversion
        collected_data.update({
            keyword: collected_data.pop(self._get_mapped_keyword(keyword), default)
            for keyword, default in six.iteritems(self.spec.kwargs)
        })

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
        return (self._resource.policy_group_name() is False) or (self.dest is not None) or self.policy.is_disabled

    def _generate_full_policy_rule_name(self):
        group_name = self._resource.policy_group_name()
        rule_name = self.rule_name or self.__name__
        full_policy_rule_name = '{}:{}'.format(group_name, rule_name)
        if full_policy_rule_name not in self.policy.rules:
            raise self._error(
                exceptions.BadResourceDefinition,
                'Policy rule {} does not exist in policy file'.format(full_policy_rule_name))
        return full_policy_rule_name

    def _get_mapped_keyword(self, original_keyword):
        """Return the alternative keyword if one exists."""
        return self.keyword_map.get(original_keyword, original_keyword)

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
