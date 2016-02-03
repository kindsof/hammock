from __future__ import absolute_import
import hammock.common as common


class Credentials(dict):
    """
    Converts a headers object into a credentials dict,
    It is used by the policy.Policy class.
    """
    def __init__(self, headers):
        super(Credentials, self).__init__(
            user=headers.get(common.HEADER_USER, None),
            project_id=headers.get(common.HEADER_PROJECT_ID, None),
            roles=headers.get(common.HEADER_ROLE, '').split(';'),
        )
