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
    client_methods = None

    def _wrapper(self, req):
        """
        Wraps the decorated func (self._func)
        :param req: a hammock.types.request.Request object.
        :return: response as hammock.types.response.Response object.
        """
        if self.dest is None:
            kwargs = self._extract_kwargs(req, req.collected_data)
            self._resource.api.policy.check(self.rule_name, target=kwargs, headers=req.headers)
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
            logging.warning('[Error parsing request kwargs %s] %s', req.uid, exc)
            raise exceptions.BadRequest('Error parsing request parameters, {}'.format(exc))

    def _convert_to_kwargs(self, req, collected_data):
        args = self.spec.args[:]
        kwargs = collected_data
        kwargs.update({
            keyword: kwargs.get(keyword, default)
            for keyword, default in six.iteritems(self.spec.kwargs)
        })
        if common.KW_HEADERS in self.spec.args:
            kwargs[common.KW_HEADERS] = req.headers
        for keyword, error_msg in (
            (common.KW_FILE, 'expected {} as {}'.format(common.CONTENT_TYPE, common.TYPE_OCTET_STREAM)),
            (common.KW_LIST, 'expected {} {} as list'.format(common.CONTENT_TYPE, common.TYPE_JSON)),
        ):
            if keyword in args:
                try:
                    kwargs[keyword] = req.collected_data[keyword]
                except KeyError:
                    raise exceptions.BadData(error_msg)
                args.remove(keyword)
        missing = set(args) - set(kwargs)
        if missing:
            raise exceptions.BadRequest('Missing parameters: {}'.format(', '.join(missing)))
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
