#!/usr/bin/env bash

influx write -b test -f /docker-entrypoint-initdb.d/test_data.txt
