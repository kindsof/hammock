from __future__ import absolute_import
import hammock
import hammock.client as client
import hammock.doc as doc


class CommonResources(hammock.Resource):

    PATH = ''
    POLICY_GROUP_NAME = False

    @hammock.get('_client', response_content_type='text/x-python')
    def get_client(self, _host):
        return client.ClientGenerator('Client', self.params['_resource_package'], _host).code

    @hammock.get('_api')
    def get_api(self):
        return doc.generate(self.params['_resource_package'])
