from __future__ import absolute_import
import six
import functools
import collections
import re
import logging
import hammock.common as common
from . import backend


LOG = logging.getLogger(__name__)


class AWeb(backend.Backend):

    def _add_route_methods(self, resource, base_path):
        paths = collections.defaultdict(dict)
        for route_method in common.iter_route_methods(resource):
            falcon_method = 'on_{}'.format(route_method.method.lower())
            paths[route_method.path][falcon_method] = functools.partial(route_method.responder, resource)
        for route_path, methods in six.iteritems(paths):
            self._add_route(base_path, resource.name(), route_path, methods)

    def _add_sink_methods(self, resource, base_path):
        sinks = {}
        for method in common.iter_sink_methods(resource):
            full_path = '/' + common.url_join(base_path, resource.name(), method.path)
            pattern = re.compile(common.CONVERT_PATH_VARIABLES(full_path))
            sinks[pattern] = method.method
        for pattern in self._sort_sinks(sinks):
            self._api.add_sink(functools.partial(sinks[pattern], resource), pattern)
            LOG.debug('Added sink %s for %s', pattern.pattern, repr(sinks[pattern].__code__))
