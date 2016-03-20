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


def colorize(color, val):
    if ENABLED:
        codes = CODES[color]
        val = codes[0] + val + codes[1]
    return val


def factory(color):
    return functools.partial(colorize, color)
