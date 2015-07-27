import hammock.common as common
import hammock.types as types
import requests
import logging
import urlparse
import functools
import inspect


def sink(path="", dest=None, pre_process=None, post_process=None, trim_prefix=False):
    def _decorator(func):
        func.is_sink = True
        func.path = path
        func.dest = dest
        if func.dest:
            _func_is_pass(func)

        def _full_path_wrapper(full_path):
            @functools.wraps(func)
            def _wrapper(request, response):
                logging.info("Redirecting %s", request.url)
                if trim_prefix:
                    _trim_prefix(request, full_path)
                if pre_process:
                    pre_process(request)
                if func.dest:
                    output = _passthrough(request, func.dest)
                else:
                    output = func(request)
                if post_process:
                    output = post_process(output)
                body_or_stream, response._headers, response.status = output
                response.status = str(response.status)
                if hasattr(body_or_stream, "read"):
                    response.stream = body_or_stream
                else:
                    response.body = body_or_stream
            return _wrapper
        func.get = _full_path_wrapper
        return func
    return _decorator


def iter_sink_methods(resource_object):
    return (
        attr for _, attr in inspect.getmembers(resource_object)
        if getattr(attr, "is_sink", False)
    )


def _passthrough(request, dest):
    redirection_url = common.url_join(dest, request.path)
    logging.info("Passthrough to %s", redirection_url)
    inner_request = requests.Request(
        request.method,
        url=redirection_url,
        data=request.stream if request.method in ("POST", "PUT", "PATCH") else None,
        headers={
            k: v if k.lower() != "host" else urlparse.urlparse(dest).netloc
            for k, v in request.headers.iteritems()
            if v != ""
        },
    )
    session = requests.Session()
    try:
        prepared = session.prepare_request(inner_request)
        if request.headers.get('CONTENT-LENGTH'):
            prepared.headers['CONTENT-LENGTH'] = request.headers.get('CONTENT-LENGTH')
        if request.headers.get('TRANSFER-ENCODING'):
            del prepared.headers['TRANSFER-ENCODING']

        inner_response = session.send(prepared, stream=True)
        return types.Response(inner_response.raw, inner_response.headers, inner_response.status_code)
    finally:
        session.close()


def _trim_prefix(request, prefix):
    request.path = request.path[len(prefix):]


def _func_is_pass(func):
    lines = [line.strip() for line in inspect.getsource(func).split("\n")]
    while not lines.pop(0).startswith("def"):
        pass
    empty = "".join(lines).strip() == "pass"
    if not empty:
        raise Exception("Passthrough function %s is not empty", func.__name__)
