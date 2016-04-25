from __future__ import absolute_import
import falcon
import os
import json

import files.file as file

class Files:

    def on_get(self, req, resp):
        """List files"""
        # First, extract request arguments
        path = req.get_param('path', required=True)
        type = req.get_param('type', default=None)
        sort = req.get_param('sort', default='modified')
        reverse = req.get_param('reverse', default=False)
        reverse = reverse == 'True'

        # Here we actually do stuff
        try:
            result = [a_file.to_dict for a_file in file.list(path, type, sort, reverse)]
        except OSError:
            raise falcon.HTTPNotFound('No path {}'.format(path))

        # Least, prepare the response
        result_string = json.dumps(result)
        resp.status = falcon.HTTP_200
        resp.body = result_string
        resp.content_type = 'application/json'


application = falcon.API()

# Add the resource to the API:
application.add_route('/', Files())
