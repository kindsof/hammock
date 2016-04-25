#!/usr/bin/env bash

PYTHONPATH=../../ .venv/bin/uwsgi --yaml uwsgi-falcon.yml
