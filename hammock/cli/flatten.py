def flatten(data, separator='.', prefix=''):
    if isinstance(data, list):
        return _flatten_list(data, separator, prefix)
    elif isinstance(data, dict):
        return _flatten_dict(data, separator, prefix)
    else:
        return {prefix or 'value': data}


def _flatten_dict(data, separator, prefix):
    return {
        prefix + separator + flat_key if prefix else flat_key: flat_value
        for key, value in data.items()
        for flat_key, flat_value in flatten(value, separator, key).items()
    }


def _flatten_list(data, separator, prefix):
    return {
        prefix + separator + str(i) + separator + flat_key: flat_value
        for i, value in enumerate(data)
        for flat_key, flat_value in flatten(value, separator).items()
        }
