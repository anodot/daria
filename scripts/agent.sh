#!/usr/bin/env bash


function check_cmd() {
    cmd=$(echo $1 | awk ' { print $1; } ')
    if ! $1 >/dev/null 2>&1; then
        echo "Error: $cmd is either not installed, not in \$PATH, or not running!"
        exit 1
    fi
}

# checks to make sure docker is available
check_cmd "docker version"

# If compose is included in docker, then uses it, else uses docker-compose
$(docker compose version)
if [[ $? == 0 ]]; then
  COMPOSE=(docker compose)
else
  check_cmd "docker-compose --version"
  COMPOSE=(docker-compose)
fi
echo "Using \"$COMPOSE\" for script"

set -e

if [[ $1 == 'install' ]]; then
  $COMPOSE pull && $COMPOSE up -d
elif [[ $1 == 'upgrade' ]]; then
  $COMPOSE pull && $COMPOSE up -d && sleep 30 && docker exec -i anodot-agent agent pipeline update
elif [[ $1 == 'run' ]]; then
  $COMPOSE up -d && docker exec -it anodot-agent bash
elif [[ $1 == 'set-heap-size' ]]; then
  if ! [[ $2 =~ ^[0-9]+$ ]]; then
    echo "Please use only integers to set the heap size"
    exit 1
  fi
  sed -i -E 's/SDC_JAVA_OPTS.*/SDC_JAVA_OPTS: "-Xmx'$2'm -Xms'$2'm -server"/' docker-compose.yml
elif [[ $1 == 'set-thread-pool-size' ]]; then
  if ! [[ $2 =~ ^[0-9]+$ ]]; then
    echo "Please use only integers to set the thread pool size"
    exit 1
  fi
  sed -i -E 's/SDC_CONF_RUNNER_THREAD_POOL_SIZE.*/SDC_CONF_RUNNER_THREAD_POOL_SIZE: "'$2'"/' docker-compose.yml
elif [[ $1 == 'apply' ]]; then
  docker exec -i anodot-agent rm -rf /agent-data
  docker cp ./agent-data anodot-agent:/agent-data
  docker exec --user root anodot-agent chown -R agent:agent /agent-data
  docker exec -i anodot-agent agent apply -d /agent-data
elif [[ $1 == 'diagnostics-info' ]]; then
  dest_path="./agent-diagnostics-info"
  [ ! -d $dest_path ] && mkdir $dest_path
  flags=""
  [ -n "$2" ] && [ $2 == '--plain-text-credentials' ] && flags="--plain-text-credentials"

  echo "Exporting configs"
  docker exec anodot-agent agent streamsets export --dir-path=/tmp/streamsets
  docker cp anodot-agent:/tmp/streamsets $dest_path/ && docker exec anodot-agent rm -r /tmp/streamsets
  echo "Copied to the $dest_path"
  echo "Deleted /tmp/streamsets"
  docker exec anodot-agent agent source export --dir-path=/tmp/sources $flags
  docker cp anodot-agent:/tmp/sources $dest_path/ && docker exec anodot-agent rm -r /tmp/sources
  echo "Copied to the $dest_path"
  echo "Deleted /tmp/sources"
  docker exec anodot-agent agent pipeline export --dir-path=/tmp/pipelines
  docker cp anodot-agent:/tmp/pipelines $dest_path/ && docker exec anodot-agent rm -r /tmp/pipelines
  echo "Copied to the $dest_path"
  echo "Deleted /tmp/pipelines"

  echo "Exporting logs"
  log_path=$(docker exec anodot-agent bash -c 'echo "$LOG_FILE_PATH"') && docker cp anodot-agent:$log_path $dest_path
  docker logs anodot-agent >& $dest_path/agent-container.log
  echo "Exported anodot-agent logs to the $dest_path/agent-container.log"
  docker logs anodot-sdc >& $dest_path/sdc-container.log
  echo "Exported anodot-sdc logs to the $dest_path/sdc-container.log"

  info_file=$dest_path/system_info.txt
  touch $info_file
  echo "Average load" >> $info_file
  docker exec anodot-agent cat /proc/loadavg >> $info_file
  echo "" >> $info_file
  docker exec anodot-agent lscpu | grep 'CPU(s):' >> $info_file
  echo "" >> $info_file
  echo "Memory usage in MB" >> $info_file
  docker exec anodot-agent free -m >> $info_file
  echo "Exported system info to the $info_file"

  echo "Exporting containers info"
  docker inspect anodot-agent >& $dest_path/agent-container-info.txt
  echo "Exported agent container info to the $dest_path/agent-container-info.txt"
  docker inspect anodot-sdc >& $dest_path/streamsets-container-info.txt
  echo "Exported streamsets container info to the $dest_path/streamsets-container-info.txt"

  echo "Archiving"
  tar -czvf agent-diagnostics-info.tar $dest_path
  rm -r $dest_path

  echo "Exported anodot-agent diagnostics info to the agent-diagnostics-info.tar archive"
else
  echo "Wrong command supplied. Please use ./agent [install|run|upgrade|set-heap-size|set-thread-pool-size|apply]"
fi
