#!/usr/bin/env bash

influx write -b test -f /docker-entrypoint-initdb.d/test_data.txt
BUCKET_ID=$(influx bucket list | grep test | awk '{printf $1}')
influx v1 dbrp create --db test --bucket-id $BUCKET_ID --rp 0 --default
