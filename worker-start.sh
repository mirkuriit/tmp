#!/bin/sh
set -e
exec poetry run celery --app src.worker worker --loglevel info