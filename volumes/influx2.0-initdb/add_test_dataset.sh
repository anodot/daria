#!/usr/bin/env bash

# add test data
influx write -b test -f /docker-entrypoint-initdb.d/test_data.txt
BUCKET_ID=$(influx bucket list | grep test | awk '{printf $1}')
# map for influxdb 1.x compatibility
influx v1 dbrp create --db test --bucket-id $BUCKET_ID --rp 100000 --default
# create influxdb 1.x compatibility authentication
influx v1 auth create --read-bucket $BUCKET_ID --username test --password testtest
