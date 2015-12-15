class ResourceNode(object):
    """
    A directional graph of nodes.
    """

    def add(self, name, node=None):
        node = node or ResourceNode()
        if not hasattr(self, name):
            setattr(self, name, node)
        return getattr(self, name)

    def get_node(self, walk_node_names):
        node = self
        for name in walk_node_names:
            node = node.add(name)
        return node
