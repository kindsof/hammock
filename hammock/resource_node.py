class ResourceNode(object):

    def add(self, name, resource=None):
        resource = resource or ResourceNode()
        if not hasattr(self, name):
            setattr(self, name, resource)
        return getattr(self, name)
