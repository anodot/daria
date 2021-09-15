#!/usr/bin/env bash

set -e
set -u

sleep 5 && alembic merge heads && alembic upgrade head

exec /entrypoint.sh "$@"
