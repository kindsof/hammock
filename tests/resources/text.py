from hammock import resource


class Text(resource.Resource):

    @resource.get("upper/{text}")
    def upper(self, text):  # pylint: disable=unused-argument
        return text.upper()

    @resource.get("replace/{text}")
    def replace(self, text, old, new):  # pylint: disable=unused-argument
        return text.replace(old, new)

    @resource.put("replace/{text}")
    def replace_put(self, text, old, new):  # pylint: disable=unused-argument
        return text.replace(old, new)

    @resource.post("replace/{text}")
    def replace_post(self, text, old, new):  # pylint: disable=unused-argument
        return text.replace(old, new)

    @resource.delete("replace/{text}")
    def replace_delete(self, text, old, new):  # pylint: disable=unused-argument
        return text.replace(old, new)

    @resource.get("raise_exception")
    def raise_exception(self):  # pylint: disable=unused-argument
        raise Exception("This exeption is intentional")
