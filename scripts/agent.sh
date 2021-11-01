#!/usr/bin/env bash

set -e

function check_cmd() {
    cmd=$(echo $1 | awk ' { print $1; } ')
    if ! $1 >/dev/null 2>&1; then
        echo "Error: $cmd is either not installed, not in \$PATH, or not running!"
        exit 1
    fi
}

# checks to make sure docker and docker-compose are available   
check_cmd "docker version"
check_cmd "docker-compose --version"

if [[ $1 == 'install' ]]; then
  docker-compose pull && docker-compose up -d
elif [[ $1 == 'upgrade' ]]; then
  docker-compose pull && docker-compose up -d && sleep 30 && docker exec -i anodot-agent agent pipeline update
elif [[ $1 == 'run' ]]; then
    docker-compose up -d && docker exec -it anodot-agent bash
elif [[ $1 == 'set-heap-size' ]]; then
  if ! [[ $2 =~ ^[0-9]+$ ]]; then
    echo "Please use only integers to set the heap size"
    exit 1
  fi
  sed -i '' -E 's/SDC_JAVA_OPTS.*/SDC_JAVA_OPTS: "-Xmx'$2'm -Xms'$2'm -server"/' docker-compose.yaml
elif [[ $1 == 'set-thread-pool-size' ]]; then
  if ! [[ $2 =~ ^[0-9]+$ ]]; then
    echo "Please use only integers to set the thread pool size"
    exit 1
  fi
  sed -i '' -E 's/SDC_CONF_RUNNER_THREAD_POOL_SIZE.*/SDC_CONF_RUNNER_THREAD_POOL_SIZE: "'$2'"/' docker-compose.yaml
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
  tar -cvf agent-diagnostics-info.tar $dest_path
  rm -r $dest_path

  echo "Exported anodot-agent diagnostics info to the agent-diagnostics-info.tar archive"
elif [[ $1 == 'kuber-diagnostics-info' ]]; then
  POD=$(kubectl get pod -l app.kubernetes.io/name=anodot-agent -o jsonpath="{.items[0].metadata.name}")
  dest_path="./agent-diagnostics-info"
  [ ! -d $dest_path ] && mkdir $dest_path
  flags=""
  [ -n "$2" ] && [ $2 == '--plain-text-credentials' ] && flags="--plain-text-credentials"

  echo "Exporting configs"
  kubectl exec $POD -- agent streamsets export --dir-path=/tmp/streamsets
  kubectl cp $POD:/tmp/streamsets $dest_path/ && kubectl exec $POD -- rm -r /tmp/streamsets
  echo "Copied to the $dest_path"
  echo "Deleted /tmp/streamsets"
  kubectl exec $POD -- agent source export --dir-path=/tmp/sources $flags
  kubectl cp $POD:/tmp/sources $dest_path/ && kubectl exec $POD -- rm -r /tmp/sources
  echo "Copied to the $dest_path"
  echo "Deleted /tmp/sources"
  kubectl exec $POD -- agent pipeline export --dir-path=/tmp/pipelines
  kubectl cp $POD:/tmp/pipelines $dest_path/ && kubectl exec $POD -- rm -r /tmp/pipelines
  echo "Copied to the $dest_path"
  echo "Deleted /tmp/pipelines"

  echo "Exporting logs"
  log_path=$(kubectl exec $POD -- bash -c 'echo "$LOG_FILE_PATH"') && kubectl cp $POD:$log_path $dest_path/agent.log
  echo "Exported agent application logs to the $dest_path/agent.log"
  kubectl logs $POD >& $dest_path/agent-container.log
  echo "Exported anodot-agent logs to the $dest_path/agent-container.log"
  kubectl get pods -o custom-columns=":metadata.name" | grep streamsets-agent | while read -r pod ; do
    kubectl logs $pod >& $dest_path/$pod.log
  done
  echo "Exported streamsets logs to the ./agent-diagnostics-info/ directory"

  info_file=$dest_path/system_info.txt
  touch $info_file
  echo "Average load" >> $info_file
  kubectl exec $POD -- cat /proc/loadavg >> $info_file
  echo "" >> $info_file
  kubectl exec $POD -- lscpu | grep 'CPU(s):' >> $info_file
  echo "" >> $info_file
  echo "Memory usage in MB" >> $info_file
  kubectl exec $POD -- free -m >> $info_file
  echo "Exported system info to the $info_file"

  kubectl get pod $POD -o yaml > $dest_path/agent-container-info.txt
  echo "Exported agent pod info to the $dest_path/agent-container-info.txt"
  echo "Exporting streamsets pods info"
  kubectl get pods -o custom-columns=":metadata.name" | grep streamsets-agent | while read -r pod ; do
    kubectl get pod $pod -o yaml > $dest_path/$pod-container-info.txt
  done

  echo "Archiving"
  tar -cvf agent-diagnostics-info.tar $dest_path
  rm -r $dest_path

  echo "Exported anodot-agent diagnostics info to the agent-diagnostics-info.tar archive"
else
  echo "Wrong command supplied. Please use ./agent [install|run|upgrade|set-heap-size|set-thread-pool-size|apply]"
fi
