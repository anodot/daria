#!/usr/bin/env bash

docker exec agent-kafka bash -c "kafka-console-producer.sh --broker-list localhost:9092 --topic test_value_const < /home/test_json_items"
docker exec agent-kafka bash -c "kafka-console-producer.sh --broker-list localhost:9092 --topic test_timestamp_ms < /home/test_json_items"
docker exec agent-kafka bash -c "kafka-console-producer.sh --broker-list localhost:9092 --topic test_timestamp_string < /home/test_json_items"
docker exec agent-kafka bash -c "kafka-console-producer.sh --broker-list localhost:9092 --topic test_timestamp_kafka < /home/test_json_items"
