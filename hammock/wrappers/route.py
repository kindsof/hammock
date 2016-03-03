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

    success_code = 200,
    response_content_type = common.TYPE_JSON,  # XXX: This should be removed.
    keyword_map = None
    client_methods = None

    def __init__(self, func):
        wrapper.Wrapper.__init__(self, func)
        self._validate_keyword_map()

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
            if common.KW_HEADERS in self.spec.args:
                kwargs[common.KW_HEADERS] = req.headers
            result = self(**kwargs)  # pylint: disable=not-callable
            resp = response.Response.from_result(result, self.success_code)
        else:
            resp = proxy.proxy(req, self.dest)
        return resp

    def _extract_kwargs(self, req, collected_data):
        try:
            kwargs = self._convert_to_kwargs(req, collected_data)
            logging.debug('[kwargs %s] %s', req.uid, kwargs)
            return kwargs
        except exceptions.HttpError:
            raise
        except Exception as exc:  # pylint: disable=broad-except
            logging.exception('[Error parsing request kwargs %s] %s', req.uid, exc)
            raise exceptions.BadRequest('Error parsing request parameters, {}'.format(exc))

    def _convert_to_kwargs(self, req, collected_data):
        args = list(set(self.spec.args[:]) - {common.KW_CREDENTIALS, common.KW_ENFORCER, common.KW_HEADERS})
        kwargs = collected_data
        if common.KW_HEADERS in self.spec.args:
            kwargs[common.KW_HEADERS] = req.headers

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

        missing = set([self._get_mapped_keyword(arg) for arg in args]) - set(kwargs)
        if missing:
            raise exceptions.BadRequest('Missing parameters: {}'.format(', '.join(missing)))

        # Handle args keyword conversion
        kwargs.update({keyword: kwargs.pop(self._get_mapped_keyword(keyword)) for keyword in args})

        # Handle kwargs keyword conversion
        kwargs.update({keyword: kwargs.pop(self._get_mapped_keyword(keyword), default)
                       for keyword, default in six.iteritems(self.spec.kwargs)})

        return kwargs

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
            raise RuntimeError('Mapped arguments {} are not in method arguments'.format(', '.join(invalid_arguments)))

        if len(set(self.keyword_map.values())) < len(self.keyword_map):
            raise RuntimeError('Multiple keywords are mapped to the same one {}'.format(self.keyword_map))
