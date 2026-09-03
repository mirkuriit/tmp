#!/bin/sh
set -e
alembic upgrade head
exec uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 --log-level critical