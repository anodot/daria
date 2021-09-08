#!/usr/bin/env bash

set -e
set -u

docker exec -i anodot-agent rm -rf /agent-data
docker cp ./agent-data anodot-agent:/agent-data
docker exec -i anodot-agent agent apply -d /agent-data
