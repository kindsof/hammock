from __future__ import absolute_import
import munch
import hammock.common as common


class Credentials(munch.Munch):
    """
    Converts a headers object into a credentials dict,
    It is used by the policy.Policy class.
    """
    def __init__(self, headers):
        super(Credentials, self).__init__(
            user_name=headers.get(common.HEADER_USER_NAME, None),
            user_id=headers.get(common.HEADER_USER_ID, None),
            project_name=headers.get(common.HEADER_PROJECT_NAME, None),
            project_id=headers.get(common.HEADER_PROJECT_ID, None),
            user_domain_name=headers.get(common.HEADER_USER_DOMAIN_NAME, None),
            user_domain_id=headers.get(common.HEADER_USER_DOMAIN_ID, None),
            project_domain_name=headers.get(common.HEADER_PROJECT_DOMAIN_ID, None),
            project_domain_id=headers.get(common.HEADER_PROJECT_DOMAIN_ID, None),
            roles=headers.get(common.HEADER_ROLES, '').split(';'),
        )
