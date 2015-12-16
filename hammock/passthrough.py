from __future__ import absolute_import

import logging

import warnings

import hammock.common as common
import hammock.types.request as request


def passthrough(self, backend_req, backend_resp, dest, pre_process, post_process, trim_prefix, func, exception_handler, **params):
    req = request.Request.from_falcon(backend_req)
    logging.debug('[Passthrough received %s] requested: %s', req.uid, req.url)
    try:
        context = {}
        if trim_prefix:
            req.trim_prefix(trim_prefix)
        if pre_process:
            pre_process(req, context, **params)
        if dest:
            resp = req.send_to(dest)
        else:
            resp = func(self, req, **params)
        if post_process:
            resp = post_process(resp, context, **params)  # XXX: should remove the resp = once harbour will adapt
        resp.update_falcon(backend_resp)
    except Exception as exc:  # pylint: disable=broad-except
        common.log_exception(exc, req.uid)
        self.handle_exception(exc, exception_handler)
    finally:
        logging.debug(
            '[Passthrough response %s] status: %s, body: %s', req.uid, resp.status, resp.content,
        )


def send_to(req, dest):
    warnings.warn('deprecated, use req.send_to(dest) instead', DeprecationWarning)
    return req.send_to(dest)
