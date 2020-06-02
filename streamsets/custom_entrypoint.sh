#!/usr/bin/env bash

set -e
set -u

#required to overcome root readonly fs
rm -rf "${SDC_CONF}" || echo "skipping cleanup of ${SDC_CONF} ..."
cp -frv "/opt/sdc_conf" "${SDC_CONF}"

exec /docker-entrypoint.sh "$@"