#!/usr/bin/env bash

docker exec agent-kafka bash -c "kafka-console-producer.sh --broker-list localhost:9092 --topic test_csv < /home/test.csv"
docker exec agent-kafka bash -c "kafka-console-producer.sh --broker-list localhost:9092 --topic test_kfk < /home/test_json_items"

while IFS= read -r line; do
  curl -X POST localhost:9200/test/_doc/ -H 'Content-Type: application/json' -d"$line"
done < test-datasets/test_json_items
