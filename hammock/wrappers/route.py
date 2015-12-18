from __future__ import absolute_import
import six
import logging
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

    def _wrapper(self, resource, req):
        """
        Wraps the decorated func (self._func)
        :param req: a hammock.types.request.Request object.
        :return: response as hammock.types.response.Response object.
        """
        kwargs = self._extract_kwargs(req)
        result = self._func(resource, **kwargs)
        resp = response.Response.from_result(result, self.success_code)
        return resp

    def _extract_kwargs(self, req):
        try:
            kwargs = self._convert_to_kwargs(req)
            logging.debug('[kwargs %s] %s', req.uid, kwargs)
            return kwargs
        except exceptions.HttpError:
            raise
        except Exception as exc:  # pylint: disable=broad-except
            logging.warning('[Error parsing request kwargs %s] %s', req.uid, exc)
            raise exceptions.BadRequest('Error parsing request parameters, {}'.format(exc))

    def _convert_to_kwargs(self, req):
        args = self.spec.args[:]
        kwargs = req.collected_data
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
    def _get_success_code(code):
        if isinstance(code, int):
            return code
        else:
            return int(code.split(' ')[0])
