#!/usr/bin/env bash

docker exec streamsets-agent_kafka_1 bash -c "kafka-console-producer.sh --broker-list localhost:9092 --topic test < /home/test_json_items"
