from __future__ import absolute_import
import os

UWSGI_PID_FILE = '/var/run/phoenix-uwsgi.pid'
LOG_DIR = "/var/log/stratoscale"
LOG_PATH = os.path.join(LOG_DIR, "phoenix.stratolog")
LOG_FORMAT = str({"created": "${unix}",
                  "msg": "${msg}",
                  "levelno": 10,
                  "args": [],
                  "exc_text": "",
                  "levelname": "DEBUG",
                  "process": 0,
                  "threadName": "uwsgi",
                  "pathname": "/usr/bin/uwsgi",
                  "lineno": 0,
                  "module": "module",
                  "funcName": "funcName",
                  "processName": "MainProcess",
                  "name": "root",
                  "thread": 0,
                  "filename": "usr/bin/uwsgi"}) + '\n'
