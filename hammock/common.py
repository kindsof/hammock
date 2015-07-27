def url_join(*parts):
    return '/'.join(arg.strip('/') for arg in parts if arg)
