#!/usr/bin/env bash

docker exec agent-kafka bash -c "kafka-console-producer.sh --broker-list localhost:9092 --topic test_csv < /home/test.csv"
docker exec agent-kafka bash -c "kafka-console-producer.sh --broker-list localhost:9092 --topic test_kfk < /home/test_json_items"
docker exec agent-kafka bash -c "kafka-console-producer.sh --broker-list localhost:9092 --topic test_running_counters < /home/test_running_counter.txt"


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
