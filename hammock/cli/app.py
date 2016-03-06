from __future__ import absolute_import
import logging
import os
import cliff.app as app
import cliff.interactive as interactive
import hammock.cli.command_manager as command_manager


class App(app.App):

    prompt = '> '
    description = 'CLI'
    version = ''
    REQUESTS_LOGGING_LEVEL = logging.ERROR

    def __init__(self, clients, **kwargs):
        """
        Create a CLI app
        :param clients: a dict of name: hammock-client class
        """
        super(App, self).__init__(
            description=self.description,
            version=self.version,
            command_manager=command_manager.CommandManager(),
            interactive_app_factory=self._interactive_app_factory,
            **kwargs
        )
        self.client_classes = clients

    def build_option_parser(self, description, version, argparse_kwargs=None):
        parser = super(App, self).build_option_parser(description, version, argparse_kwargs)
        parser.add_argument(
            'url', nargs='?',
            default=os.environ.get('URL', 'http://localhost'),
        )
        return parser

    def initialize_app(self, argv):
        super(App, self).initialize_app(argv)
        logging.getLogger('requests').setLevel(self.REQUESTS_LOGGING_LEVEL if not self.options.debug else logging.DEBUG)
        self.LOG.debug("options: %s", self.options)
        clients = [client_class(self.options.url) for client_class in self.client_classes]
        self.command_manager.load_commands(clients)

    def _interactive_app_factory(self, *args, **kwargs):
        interactive_app = interactive.InteractiveApp(*args, **kwargs)
        interactive_app.prompt = self.prompt
        return interactive_app
