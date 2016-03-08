from __future__ import absolute_import
import hammock


class Auth(hammock.Resource):

    POLICY_GROUP_NAME = False

    @hammock.post()
    def login(self, username, password, tenant):  # pylint: disable=unused-argument
        return True

    @hammock.delete()
    def logout(self, _headers, token=None):  # pylint: disable=unused-argument
        return True

    @hammock.get()
    def status(self, _headers, token=None):  # pylint: disable=unused-argument
        return True

    @hammock.put()
    def refresh(self, _headers, token=None):  # pylint: disable=unused-argument
        return True
