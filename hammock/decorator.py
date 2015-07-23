import falcon
import inspect
import functools
import simplejson as json
import logging
import uuid


KW_HEADERS = "_headers"
KW_FILE = "_file"
KW_LIST = "_list"
CONTENT_TYPE = "content-type"
TYPE_JSON = "application/json"
TYPE_OCTET_STREAM = "application/octet-stream"


def route(path, method, client_methods=None, success_code=falcon.HTTP_200, result_content_type=TYPE_JSON):
    def _decorator(func):
        spec = inspect.getargspec(func)
        func.is_route = True
        func.path = path
        func.method = method
        func.client_methods = client_methods
        func.success_code = int(
            success_code.split(" ")[0] if not isinstance(success_code, int) else success_code)
        func.result_content_type = result_content_type

        @functools.wraps(func)
        def _wrapper(self, request, response, **url_kwargs):
            request_uuid = uuid.uuid4()
            request_params, header_handler = _extract_request_params(request)
            kwargs = _arrange_params_by_spec(spec, url_kwargs, request_params, header_handler)
            logging.debug(
                "[request %s] %s %s, kwargs=%s (%s ommitted)",
                request_uuid, request.method, request.url, kwargs, KW_HEADERS)
            try:
                result = func(self, **kwargs)  # pylint: disable=star-args
                headers = {}
                if isinstance(result, dict) and KW_HEADERS in result:
                    headers = result[KW_HEADERS]
                    del result[KW_HEADERS]
            except Exception as e:
                e = _convert_exception_of_internal_function(e)
                response.status, response.body = e.status, e.to_dict()  # assingment for logging in finally block
                raise e
            else:
                for k, v in headers.iteritems():
                    response.set_header(k, v)
                if result is not None:
                    if result_content_type == TYPE_JSON:
                        response.body = json.dumps(result)
                    elif result_content_type == TYPE_OCTET_STREAM:
                        response.stream = result
                    response.set_header(CONTENT_TYPE, result_content_type)
                response.status = success_code
            finally:
                logging.debug(
                    "[response %s] status: %s, body: %s",
                    request_uuid, response.status, response.body,
                )

        func.responder = _wrapper
        return func
    return _decorator


def _extract_request_params(request):
    params = {
        k: (v if v != "None" else None)
        for k, v in request.params.iteritems()
    }
    if request.method in ("PUT", "POST"):
        content_type = request.get_header(CONTENT_TYPE)
        if content_type == TYPE_JSON:
            try:
                data = json.load(request.stream)
                if type(data) == dict:
                    params.update(data)
                elif type(data) == list:
                    params[KW_LIST] = data
            except (ValueError, UnicodeDecodeError):
                raise falcon.HTTPError(
                    falcon.HTTP_753,
                    'Malformed JSON',
                    'Could not decode the request body. The JSON was incorrect or not encoded as UTF-8.'
                )
        else:
            params[KW_FILE] = request.stream
    return params, request.get_header


def _arrange_params_by_spec(spec, url_kwargs, request_params, header_handler):
    defaults = spec.defaults or []
    args = spec.args[1:len(spec.args) - len(defaults)]
    keywords = spec.args[len(spec.args) - len(defaults):]
    request_params = request_params or {}
    if spec.keywords:
        kwargs = {spec.keywords: request_params}
    else:
        kwargs = {
            keyword: request_params.get(keyword, default)
            for keyword, default in zip(keywords, defaults)
        }

    url_kwargs.update(request_params or {})
    kwargs.update({arg: url_kwargs.get(arg, None) for arg in args})
    if KW_HEADERS in args:
        kwargs[KW_HEADERS] = header_handler
    for kw, error_msg in (
        (KW_FILE, "expected {} as {}".format(CONTENT_TYPE, TYPE_OCTET_STREAM)),
        (KW_LIST, "expected {} {} as list".format(CONTENT_TYPE, TYPE_JSON)),
            ):
        if kw in args:
            try:
                kwargs[kw] = request_params[kw]
            except KeyError:
                raise falcon.HTTPError(falcon.HTTP_415, 'Bad data', error_msg)
            args.remove(kw)
    missing = set(args) - set(url_kwargs or {}) - set([KW_HEADERS])
    if missing:
        raise falcon.HTTPBadRequest(
            "Missing parameters: %s" % ", ".join(missing),
            "Bad request")
    return kwargs


def _convert_exception_of_internal_function(e):
    logging.exception("Caught internal server exception")  # this will show traceback in logs
    if not issubclass(type(e), falcon.HTTPError):
        e = falcon.HTTPError(
            falcon.HTTP_500,
            "Internal Server Error",
            "Got exception in internal function: %s" % e,
        )
    return e


def iter_route_methods(resource_object):
    return (
        attr for _, attr in inspect.getmembers(resource_object)
        if getattr(attr, "is_route", False)
    )
