if [[ $1 == 'install' ]]; then
  docker-compose pull && docker-compose up -d
elif [[ $1 == 'run' || $1 == 'rerun' ]]; then
    docker-compose up -d
elif [[ $1 == 'attach' ]]; then
  docker attach anodot-agent
elif [[ $1 == 'set-heap-size' ]]; then
  if ! [[ $2 =~ ^[0-9]+$ ]]; then
    echo "Please use only integers to set the heap size"
    exit 1
  fi
  sed -i '' -E 's/SDC_JAVA_OPTS.*/SDC_JAVA_OPTS: "-Xmx'$2'm -Xms'$2'm -server"/' docker-compose.yaml
  docker-compose up -d
elif [[ $1 == 'set-thread-pool-size' ]]; then
  if ! [[ $2 =~ ^[0-9]+$ ]]; then
    echo "Please use only integers to set the thread pool size"
    exit 1
  fi
  sed -i '' -E 's/SDC_CONF_RUNNER_THREAD_POOL_SIZE.*/SDC_CONF_RUNNER_THREAD_POOL_SIZE: "'$2'"/' docker-compose.yaml
  docker-compose up -d
else
  echo "Wrong command supplied. Please use ./agent [install|run|rerun|attach|set-heap-size|set-thread-pool-size]"
fi
