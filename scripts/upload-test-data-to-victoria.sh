#!/usr/bin/env bash

curl -X POST http://victoriametrics:8428/api/v1/import -T test-datasets/test_victoria.jsonl
