from __future__ import absolute_import

import os
import cliff.interactive as interactive
import readline


class Interact(interactive.InteractiveApp):

    def __init__(self, *args, **kwargs):
        interactive.InteractiveApp.__init__(self, *args, **kwargs)
        self.prompt = self.parent_app.PROMPT
        if self.parent_app.WELCOME:
            self.stdout.write(self.parent_app.WELCOME)
        if self.parent_app.HELP:
            self.stdout.write(self.parent_app.HELP)
        self._load_history()

    def _cmdloop(self, intro=None):
        try:
            interactive.InteractiveApp._cmdloop(self, intro)
        finally:
            self._save_history()

    def _load_history(self):
        if not self.parent_app.HISTORY_FILE:
            return
        if os.path.exists(self.parent_app.HISTORY_FILE):
            with open(self.parent_app.HISTORY_FILE, 'r') as history_file:
                self.history.extend([line.strip() for line in history_file.readlines()])
            readline.read_history_file(self.parent_app.HISTORY_FILE)

    def _save_history(self):
        if not self.parent_app.HISTORY_FILE:
            return
        readline.write_history_file(self.parent_app.HISTORY_FILE)
