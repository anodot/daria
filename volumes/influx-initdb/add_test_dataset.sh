#!/usr/bin/env bash

curl -i -XPOST 'http://localhost:8086/write?db=test' -u admin:admin --data-binary @'/docker-entrypoint-initdb.d/test_data.txt'