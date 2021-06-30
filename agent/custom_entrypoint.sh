#!/usr/bin/env bash

set -e
set -u

sleep 5 && alembic upgrade head

OPEN_SSL_VERSION="${OPEN_SSL_VERSION:-1.1.1}"
if [[ $OPEN_SSL_VERSION == '1.0.2k' ]]; then
  mv /usr/bin/openssl /usr/bin/openssl.old
  mv /usr/include/openssl /usr/include/openssl.old

  ln -s /usr/local/openssl-1.0.2k/bin/openssl /usr/bin/openssl
  ln -s /usr/local/openssl-1.0.2k/include/openssl/ /usr/include/openssl
  echo /usr/local/openssl-1.0.2k/lib/ > /etc/ld.so.conf
fi

exec /entrypoint.sh "$@"
