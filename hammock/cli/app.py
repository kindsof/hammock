from __future__ import absolute_import
import logging
import os
import requests
import cliff.app as app
import cliff.interactive as interactive
from . import command_manager as command_manager


class App(app.App):

    prompt = '> '
    description = 'CLI'
    version = ''
    REQUESTS_LOGGING_LEVEL = logging.ERROR
    ENV_URL = 'URL'
    DEFAULT_URL = 'http://localhost'
    REMOVE_COMMANDS_WITH_NAME_FALSE = True

    def __init__(self, client, **kwargs):
        """
        Create a CLI app
        :param client: A hammock client
        """
        super(App, self).__init__(
            description=self.description,
            version=self.version,
            command_manager=command_manager.CommandManager(self.REMOVE_COMMANDS_WITH_NAME_FALSE),
            interactive_app_factory=self._interactive_app_factory,
            **kwargs
        )
        self.client_class = client
        self.client = None
        self.session = requests.Session()

    def build_option_parser(self, description, version, argparse_kwargs=None):
        parser = super(App, self).build_option_parser(description, version, argparse_kwargs)
        parser.add_argument(
            'url', nargs='?',
            default=os.environ.get(self.ENV_URL, self.DEFAULT_URL),
            help='(env {}) Server connection URL, default: {}.'.format(self.ENV_URL, self.DEFAULT_URL),
        )
        parser.add_argument(
            '--headers', default='',
            help='Comma separated list of colon separated key-value client headers.'
        )
        return parser

    def initialize_app(self, argv):
        """
        Initialize:
        - Parse argv into self.options.
        - Update headers in self.session from argv.
        - Initialize self.client with parsed options.
        - Loads the commands from the client.
        """
        super(App, self).initialize_app(argv)
        self.LOG.debug("options: %s", self.options)
        self.LOG.info('Destination URL: %s', self.options.url)
        logging.getLogger('requests').setLevel(self.REQUESTS_LOGGING_LEVEL if not self.options.debug else logging.DEBUG)
        self._set_headers()
        self.client = self.client_class(url=self.options.url, session=self.session)
        self.command_manager.load_commands(self.client)

    def _set_headers(self):
        headers = [header.split(':') for header in self.options.headers.split(',') if ':' in header]
        if headers:
            self.LOG.info('Using request headers:\n%s', '\n'.join([': '.join(header) for header in headers]))
        self.session.headers.update(dict(headers))

    def _interactive_app_factory(self, *args, **kwargs):
        interactive_app = interactive.InteractiveApp(*args, **kwargs)
        interactive_app.prompt = self.prompt
        return interactive_app
