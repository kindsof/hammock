from __future__ import absolute_import
import six
try:
    import ujson as json
except ImportError:
    import json


def to_bool(value):
    """
    Converts value to bool.
    Unlike bool(value), this one converts strings differently.
    Only 'True' or 'true' will be converted to True,
    all other strings will be converted to False.
    :param value: Value to convert.
    :return bool: Boolean value of value.
    """
    if isinstance(value, six.string_types):
        value = value in {'true', 'True'}
    return bool(value)


def to_list(value):
    """Converts anything to a list"""
    if not isinstance(value, list):
        return [value] if value is not None else []
    return value


def to_dict(value):
    if isinstance(value, six.string_types):
        value = json.loads(value)
    return value


def to_int(value):
    return int(value) if value is not None else None


def to_float(value):
    return float(value) if value is not None else None


def to_str(value):
    return str(value) if value is not None else None


def to_none(value):  # pylint: disable=unused-argument
    return None
