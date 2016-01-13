from hammock import resource


class Exceptions(resource.Resource):

    @resource.get('internal')
    def internal(self):
        raise Exception("This exception is intentional")
