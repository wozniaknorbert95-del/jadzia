#!/usr/bin/env bash
set -e
cd /opt/jadzia
export PYTHONPATH=/opt/jadzia
exec venv/bin/python deployment/retry-calendar-publish.py "$@"
