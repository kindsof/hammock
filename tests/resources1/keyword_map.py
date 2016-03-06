from __future__ import absolute_import

import hammock


class KeywordMap(hammock.Resource):
    """Resource used to test keyword map feature."""

    POLICY_GROUP_NAME = False

    @hammock.post(keyword_map={'valid1': 'in-valid1', 'valid2': 'in-valid2'})
    def post(self, valid1, valid2=None):
        return {'valid1': valid1, 'valid2': valid2}

    @hammock.get(keyword_map={'valid1': 'in-valid1', 'valid2': 'in-valid2'})
    def get(self, valid1, valid2=None):
        return {'valid1': valid1, 'valid2': valid2}
