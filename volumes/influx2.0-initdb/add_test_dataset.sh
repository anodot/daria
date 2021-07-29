#!/usr/bin/env bash

curl -i -XPOST 'http://localhost:8086/write?bucket=test&org=test' -u test:testtest --data-binary @'/docker-entrypoint-initdb.d/test_data.txt'
