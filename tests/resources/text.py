from __future__ import absolute_import
import hammock


class Text(hammock.Resource):

    @hammock.get("upper/{text}")
    def upper(self, text):  # pylint: disable=unused-argument
        return text.upper()

    @hammock.get("replace/{text}")
    def replace(self, text, old, new):  # pylint: disable=unused-argument
        return text.replace(old, new)

    @hammock.put("replace/{text}")
    def replace_put(self, text, old, new):  # pylint: disable=unused-argument
        return text.replace(old, new)

    @hammock.post("replace/{text}")
    def replace_post(self, text, old, new):  # pylint: disable=unused-argument
        return text.replace(old, new)

    @hammock.delete("replace/{text}")
    def replace_delete(self, text, old, new):  # pylint: disable=unused-argument
        return text.replace(old, new)

    @hammock.get("raise_exception")
    def raise_exception(self):  # pylint: disable=unused-argument
        raise Exception("This exeption is intentional")
