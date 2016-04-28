from __future__ import absolute_import
import munch


class Credentials(munch.Munch):
    """
    Converts a headers object into a credentials dict,
    It is used by the policy.Policy class.
    Expand this, add your own conversion and pass it to hammock
    class, in order to change the way headers are converted to credentials
    """
    def __init__(self, headers):
        super(Credentials, self).__init__(
            headers=headers,
            user_name=headers.get("username")
        )
