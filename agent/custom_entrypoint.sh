#!/usr/bin/env bash

set -e
set -u

source /root/.bashrc
sleep 5 && alembic upgrade head

exec /entrypoint.sh "$@"
