from __future__ import absolute_import
import logging
import cliff.commandmanager as commandmanager
import hammock.cli.command as command


LOG = logging.getLogger(__name__)
RESOURCE_CLASS_IGNORES = {'CLI_COMMAND_NAME', 'ROUTE_CLI_COMMAND_MAP'}
CLIENT_CLASS_IGNORES = {'token'}


class CommandManager(commandmanager.CommandManager):

    def __init__(self, clients=None):
        super(CommandManager, self).__init__(clients or [])

    def load_commands(self, clients):
        """
        This method is called by the __init__ method, to load the commands from the argument
        passed to init.
        :param clients: a list of hammock clients
        """
        for client in clients:
            self._load_client(client)

    def _load_client(self, client):
        """
        Loads a hammock client into app
        :param client: hammock client instance
        """
        for name in dir(client):
            # Get all clients' resources:
            attribute = getattr(client, name)
            if isinstance(attribute, type) or callable(attribute) or name.startswith('_') or name in CLIENT_CLASS_IGNORES:
                continue
            self._add_resource(attribute)

    def _add_resource(self, resource, commands=None):
        command_name = resource.CLI_COMMAND_NAME
        if command_name is False:
            return
        commands = (commands or []) + [command_name]
        for name in dir(resource):
            attribute = getattr(resource, name)
            if isinstance(attribute, type) or name.startswith('_') or name in RESOURCE_CLASS_IGNORES:
                continue
            if callable(attribute):
                self._add_command(attribute, commands, resource.ROUTE_CLI_COMMAND_MAP[name])
            else:
                self._add_resource(attribute, commands)

    def _add_command(self, method, commands, command_name):
        commands = commands + [command_name]
        command_type = command.factory(method, commands)
        command_name = ' '.join(commands)
        LOG.debug('Adding command: %s', command_name)
        self.add_command(command_name, command_type)
