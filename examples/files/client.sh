#!/usr/bin/env bash

PYTHONPATH=../../ .venv/bin/python -c "$(curl http://localhost:8000/_client)" "$@"
