#!/usr/bin/env bash

set -e
set -u

#required to overcome root readonly fs. When mounting volume into ${SDC_CONF}inside Kuberentes cluster,
#content of ${SDC_CONF} is wiped out, so we need to put it back
rm -rf "${SDC_CONF}" || echo "skipping cleanup of ${SDC_CONF} ..."
cp -frv /opt/sdc_conf/* "${SDC_CONF}"

exec /docker-entrypoint.sh "$@"
