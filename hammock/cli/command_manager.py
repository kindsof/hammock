from __future__ import absolute_import
import six
import logging
import cliff.commandmanager as commandmanager
from . import command as command
import hammock.names as names


LOG = logging.getLogger(__name__)
IGNORES = {'CLI_COMMAND_NAME', 'ROUTE_CLI_COMMAND_MAP', 'token', 'close'}


class CommandManager(commandmanager.CommandManager):

    def __init__(self, remove_commands_with_name_false=True, column_order=None, column_colors=None):
        """
        Loads commands from hammock clients
        :param bool remove_commands_with_name_false: Ignore packages, resources or methods that specify
            a cli_command_name == False
        """
        super(CommandManager, self).__init__('')
        self.remove_commands_with_name_false = remove_commands_with_name_false
        self.column_order = column_order
        self.column_colors = column_colors

    def load_commands(self, client):
        """
        This method is called by the __init__ method, to load the commands from the argument
        passed to init.
        :param client: a hammock clients
        """
        if isinstance(client, six.string_types):
            return
        self._load_class(client)

    def _load_class(self, instance, commands=None):
        resource_command_name = getattr(instance, 'CLI_COMMAND_NAME', '')

        def cli_command_map(func_name):
            return getattr(instance, 'ROUTE_CLI_COMMAND_MAP', {func_name: func_name})[func_name]

        if resource_command_name is False and self.remove_commands_with_name_false:
            return

        commands = (commands or []) + [
            resource_command_name
            if isinstance(resource_command_name, six.string_types)
            else names.to_command(instance.__class__.__name__)
        ]

        for name in dir(instance):
            # Get all clients' resources:
            attribute = getattr(instance, name)
            if isinstance(attribute, type) or name.startswith('_') or name in IGNORES:
                continue

            if callable(attribute):
                self._add_command(attribute, commands, cli_command_map(name))
            else:
                self._load_class(attribute, commands)

    def _add_command(self, method, commands, command_name):
        if command_name is False and self.remove_commands_with_name_false:
            return
        commands = commands + [command_name or names.to_command(method.__name__)]
        command_type = command.factory(method, self.column_order, self.column_colors)
        command_name = ' '.join([part for part in commands if part])
        LOG.debug('Adding command: %s', command_name)
        self.add_command(command_name, command_type)
