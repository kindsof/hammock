from __future__ import absolute_import
import hammock
import hammock.client as client


class CommonResources(hammock.Resource):

    PATH = ''
    POLICY_GROUP_NAME = False

    @hammock.get('_client', response_content_type='text/x-python')
    def get_client(self, _host):
        return client.ClientGenerator('Client', self.params['_resource_package'], _host).code
