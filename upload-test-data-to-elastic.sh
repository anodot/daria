#!/usr/bin/env bash

curl -X PUT "localhost:9200/test?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "timestamp_unix_ms": {
        "type": "date"
      }
    }
  }
}
'

while IFS= read -r line; do
  curl -X POST localhost:9200/test/_doc/ -H 'Content-Type: application/json' -d"$line"
done < test-datasets/test_json_items
