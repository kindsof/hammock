from __future__ import absolute_import
import logging
import os
import requests
import cliff.app as app
import cliff.interactive as interactive
import hammock.cli.command_manager as command_manager


class App(app.App):

    prompt = '> '
    description = 'CLI'
    version = ''
    REQUESTS_LOGGING_LEVEL = logging.ERROR
    ENV_URL = 'URL'
    DEFAULT_URL = 'http://localhost'

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
        self.session = requests.Session()

    def build_option_parser(self, description, version, argparse_kwargs=None):
        parser = super(App, self).build_option_parser(description, version, argparse_kwargs)
        parser.add_argument(
            'url', nargs='?',
            default=os.environ.get(self.ENV_URL, self.DEFAULT_URL),
            help='Server connection URL.',
        )
        parser.add_argument(
            '--headers', default='',
            help='Comma separated list of colon separated key-value client headers.'
        )
        return parser

    def initialize_app(self, argv):
        super(App, self).initialize_app(argv)
        logging.getLogger('requests').setLevel(self.REQUESTS_LOGGING_LEVEL if not self.options.debug else logging.DEBUG)
        self.LOG.info('Destination URL: %s', self.options.url)
        self.LOG.debug("options: %s", self.options)
        self.options.headers = [header.split(':') for header in self.options.headers.split(',') if ':' in header]
        if self.options.headers:
            self.LOG.info(
                'Using request headers:\n%s',
                '\n'.join([': '.join(header) for header in self.options.headers])
            )
        self.session.headers.update(dict(self.options.headers))
        self.command_manager.load_commands(self._clients())

    def _clients(self):
        clients = []
        for client_class in self.client_classes:
            self.LOG.debug('Loading client %s', client_class.__name__)
            clients.append(client_class(url=self.options.url, session=self.session))
        return clients

    def _interactive_app_factory(self, *args, **kwargs):
        interactive_app = interactive.InteractiveApp(*args, **kwargs)
        interactive_app.prompt = self.prompt
        return interactive_app
