from __future__ import absolute_import
import six
import inspect
import functools
import logging
import hammock.common as common
import hammock.types as types
import hammock.passthrough as passthrough_module
import hammock.exceptions as exceptions
import hammock.request as request
import hammock.response as response


# XXX: temporary workaround,
# until all dependencies will change their exceptions to hammock.exceptions.
try:
    import falcon
except ImportError:
    # fake falcon module and some specific exception, so we can except it later.
    falcon = type('falcon', (object,), {'HTTPError': type('HTTPError', (Exception,), {})})  # pylint: disable=invalid-name
# XXX


KW_HEADERS = common.KW_HEADERS


def route(path, method, client_methods=None, success_code=200, response_content_type=common.TYPE_JSON, exception_handler=None):
    def _decorator(func):
        spec = types.FuncSpec(func)
        func.is_route = True
        func.path = path
        func.method = method
        func.client_methods = client_methods
        func.success_code = success_code if isinstance(success_code, int) \
            else int(success_code.split(" ")[0])  # pylint: disable=maybe-no-member
        func.response_content_type = response_content_type

        @functools.wraps(func)
        def _wrapper(self, backend_req, backend_resp, **url_kwargs):
            req = request.Request.from_falcon(backend_req)
            kwargs = _extract_kwargs(spec, url_kwargs, req)
            try:
                result = func(self, **kwargs)
                resp = response.Response.from_result(result, success_code)
            except exceptions.HttpError:
                raise
            # XXX: temporary, until all dependencies will transfer to hammock exceptions
            except falcon.HTTPError:
                raise
            # XXX
            except Exception as exc:  # pylint: disable=broad-except
                common.log_exception(exc, req.uid)
                self.handle_exception(exc, exception_handler)
            else:
                resp.update_falcon(backend_resp)
                logging.debug('[response %s] status: %s, content: %s', req.uid, resp.status, resp.content)

        func.responder = _wrapper
        return func

    return _decorator


def passthrough(path, method, dest, pre_process=None, post_process=None, trim_prefix=False, exception_handler=None):
    def _decorator(func):
        func.is_route = True
        func.path = path
        func.method = method
        func.client_methods = {}
        func.success_code = None
        func.response_content_type = None

        @functools.wraps(func)
        def _wrapper(self, req, resp, **params):
            passthrough_module.passthrough(
                self,
                req,
                resp,
                dest,
                pre_process,
                post_process,
                trim_prefix,
                func,
                exception_handler,
                **params
            )

        func.responder = _wrapper
        return func

    return _decorator


def _extract_kwargs(spec, url_kwargs, req):
    try:
        kwargs = _convert_to_kwargs(spec, url_kwargs, req)
        logging.debug("[kwargs %s] %s", req.uid, kwargs)
        return kwargs
    except exceptions.HttpError:
        raise
    except Exception as exc:  # pylint: disable=broad-except
        logging.warning("[Error parsing request kwargs %s] %s", req.uid, exc)
        raise exceptions.BadRequest('Error parsing request parameters, {}'.format(exc))


def _convert_to_kwargs(spec, url_kwargs, req):
    args = spec.args[:]
    kwargs = req.collected_data
    kwargs.update(url_kwargs or {})
    kwargs.update({
        keyword: kwargs.get(keyword, default)
        for keyword, default in six.iteritems(spec.kwargs)
    })
    if common.KW_HEADERS in spec.args:
        kwargs[common.KW_HEADERS] = req.headers
    for keyword, error_msg in (
        (common.KW_FILE, "expected {} as {}".format(common.CONTENT_TYPE, common.TYPE_OCTET_STREAM)),
        (common.KW_LIST, "expected {} {} as list".format(common.CONTENT_TYPE, common.TYPE_JSON)),
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


def iter_route_methods(resource_object):
    return (
        attr for _, attr in inspect.getmembers(resource_object)
        if getattr(attr, "is_route", False)
    )
