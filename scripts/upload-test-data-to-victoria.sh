#!/usr/bin/env bash

curl -X POST http://localhost:8428/api/v1/import -T test-datasets/test_victoria.jsonl
