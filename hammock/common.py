import inspect
import falcon
import logging


URL_PARAMS_METHODS = {"GET", "HEAD"}
KW_HEADERS = "_headers"
KW_FILE = "_file"
KW_LIST = "_list"
CONTENT_TYPE = "content-type"
TYPE_JSON = "application/json"
TYPE_OCTET_STREAM = "application/octet-stream"
TOKEN_ENTRY = "X-Auth-Token"


def url_join(*parts):
    return '/'.join(arg.strip('/') for arg in parts if arg)


def log_exception(exc, request_uuid):
    if isinstance(exc, falcon.HTTPError):
        logging.warning("[Http %s Exception %s] %s", exc.status, request_uuid, exc.title)
    else:
        logging.exception("[Internal server error %s]", request_uuid)


def func_is_pass(func):
    lines = [line.strip() for line in inspect.getsource(func).split("\n")]
    while not lines.pop(0).startswith("def"):
        pass
    empty = "".join(lines).strip() == "pass"
    if not empty:
        raise Exception("Passthrough function %s is not empty", func.__name__)
