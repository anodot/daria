#!/bin/bash

set -e

# adding new repo to install correct postgres-client version
wget --no-check-certificate --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
# using stretch instead of `lsb_release -cs`-pgdg main as it's not working with the current version
echo "deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main" | tee  /etc/apt/sources.list.d/pgdg.list

apt update && apt install -y --reinstall vim netcat curl nano ca-certificates postgresql-client-12 librrd-dev default-mysql-client kafkacat

pip install --upgrade pip && pip install -r requirements.txt
