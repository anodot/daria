#!/usr/bin/env bash

set -e
set -u

sleep 5 && alembic upgrade head
python3 /usr/src/app/src/agent/scripts/update-pipeline-statuses.py

exec /entrypoint.sh "$@"
