#!/usr/bin/env bash

curl -X PUT -u elastic:password "localhost:9200/test?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "timestamp_string": {
        "type": "date"
      }
    }
  }
}
'

while IFS= read -r line; do
  curl -X POST -u elastic:password localhost:9200/test/_doc/ -H 'Content-Type: application/json' -d"$line"
done < test-datasets/test_json_items_for_elastic
