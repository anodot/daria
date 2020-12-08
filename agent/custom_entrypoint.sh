#!/usr/bin/env bash

set -e
set -u

sleep 5 && alembic upgrade head

exec /start.sh "$@"
