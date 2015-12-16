from __future__ import absolute_import
import warnings
import logging
import hammock.common as common
import hammock.request as request


def passthrough(self, req, response, dest, pre_process, post_process, trim_prefix, func, exception_handler, **params):
    req = request.Request.from_falcon(req)
    logging.debug('[Passthrough received %s] requested: %s', req.uid, req.url)
    try:
        context = {}
        if trim_prefix:
            req.trim_prefix(trim_prefix)
        if pre_process:
            pre_process(req, context, **params)
        if dest:
            output = req.send_to(dest)
        else:
            output = func(self, req, **params)
        if post_process:
            output = post_process(output, context, **params)
        body_or_stream, response._headers, response.status = output
        response.status = str(response.status)
        if hasattr(body_or_stream, "read"):
            response.stream = body_or_stream
        else:
            response.body = body_or_stream
    except Exception as exc:  # pylint: disable=broad-except
        common.log_exception(exc, req.uid)
        self.handle_exception(exc, exception_handler)
    finally:
        logging.debug(
            '[Passthrough response %s] status: %s, body: %s', req.uid, response.status, response.body,
        )


def send_to(req, dest):
    warnings.warn('deprecated, use req.send_to(dest) instead', DeprecationWarning)
    return req.send_to(dest)
