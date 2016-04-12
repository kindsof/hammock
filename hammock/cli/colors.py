from __future__ import absolute_import
import platform
import functools


CODES = {
    'bold': ('\x1b[1m', '\x1b[22m'),
    'cyan': ('\x1b[36m', '\x1b[39m'),
    'blue': ('\x1b[34m', '\x1b[39m'),
    'red': ('\x1b[31m', '\x1b[39m'),
    'magenta': ('\x1b[35m', '\x1b[39m'),
    'green': ('\x1b[32m', '\x1b[39m'),
    'underline': ('\x1b[4m', '\x1b[24m'),
}


ENABLED = platform.system() != 'Windows'


def colorize(color, val, prompt=False):
    if ENABLED:
        code_start, code_end = CODES[color]
        if prompt:
            # When writing color to cliff's prompt, we need to tell it that the color
            # characters do not take screen space, for the history-searching to work correctly
            # http://wiki.hackzine.org/development/misc/readline-color-prompt.html
            code_start = "\001" + code_start + "\002"
            code_end = "\001" + code_end + "\002"
        val = code_start + val + code_end
    return val


def factory(color):
    return functools.partial(colorize, color)
