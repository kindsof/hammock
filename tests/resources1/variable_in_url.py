from __future__ import absolute_import
import hammock


class VariableInUrl(hammock.Resource):

    POLICY_GROUP_NAME = False
    PATH = 'variable-in-url/{variable_name}'

    @hammock.get()
    def get(self, variable_name):
        return variable_name


class VariableFirstInUrl(hammock.Resource):

    POLICY_GROUP_NAME = False
    PATH = '{variable_name}/variable-in-url'

    @hammock.get()
    def get(self, variable_name):
        return variable_name
