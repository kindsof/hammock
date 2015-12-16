#! /usr/bin/env python
"""Phoenix entry point."""
from __future__ import absolute_import

import os
import sys
import subprocess
import configargparse
import phoenix.config as config

# Config dir path options (user or root).
CONFIG_DIR_PATHS = [os.path.expanduser('~/.config/phoenix'), '/etc/phoenix']


def main():
    """Phoenix entry point."""
    if os.getuid() != 0:
        sys.exit("you must be root in order to run 'phoenix' from command line")

    if not os.path.exists(config.LOG_DIR):
        os.mkdir(config.LOG_DIR)

    parser = configargparse.ArgumentParser()
    parser.add_argument('-u', '--uwsgi', default=_get_default_uwsgi_config())

    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument("--start", action="store_true")
    action_group.add_argument("--stop", action="store_true")
    action_group.add_argument("--reload", action="store_true")

    args = parser.parse_args()

    if args.start:
        subprocess.check_output(['uwsgi',
                                 '--yaml', args.uwsgi,
                                 "--pidfile", config.UWSGI_PID_FILE,
                                 "--logger", "file:{}".format(config.LOG_PATH),
                                 "--log-encoder", "json {}".format(config.LOG_FORMAT)])
    elif args.stop:
        subprocess.check_output(['uwsgi', "--stop", config.UWSGI_PID_FILE])

    elif args.reload:
        subprocess.check_output(['uwsgi', "--reload", config.UWSGI_PID_FILE])

    else:  # Manual run
        subprocess.check_output(['uwsgi', '--yaml', args.uwsgi,
                                 '--py-auto-reload', '1',       # Reload on changes
                                 '--workers', '1',              # Limit the number of processes
                                 '--honour-stdin'])             # Enable stdin for PDB usage


def _get_default_uwsgi_config():
    """Return the configuration file path."""
    config_dir_path = CONFIG_DIR_PATHS[0] if os.getuid() != 0 else CONFIG_DIR_PATHS[1]
    config_file_path = os.path.join(config_dir_path, 'uwsgi.yml')
    return config_file_path


if __name__ == '__main__':
    main()
