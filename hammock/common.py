import inspect
import falcon


def url_join(*parts):
    return '/'.join(arg.strip('/') for arg in parts if arg)


def convert_exception(e):
    if not issubclass(type(e), falcon.HTTPError):
        return falcon.HTTPError(
            falcon.HTTP_500,
            "Internal Server Error",
            "Got exception in internal function: {}".format(e),
        )
    return e


def func_is_pass(func):
    lines = [line.strip() for line in inspect.getsource(func).split("\n")]
    while not lines.pop(0).startswith("def"):
        pass
    empty = "".join(lines).strip() == "pass"
    if not empty:
        raise Exception("Passthrough function %s is not empty", func.__name__)
