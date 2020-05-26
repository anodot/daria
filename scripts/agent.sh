num='^[0-9]+$'

if [[ $1 == 'install' ]]; then
  cp docker-compose.base docker-compose.yaml
  sed -i '' -e "s/SDC_JAVA_OPTS_VALUE/${SDC_JAVA_OPTS} -Xmx1024m -Xms1024m -server/"
  sed -i '' -e "s/SDC_THREAD_POOL_SIZE_VALUE/50/"
  docker-compose pull && docker-compose up -d
elif [[ $1 == 'run' || $1 == 'rerun' ]]; then
    docker-compose up -d
elif [[ $1 == 'attach' ]]; then
  docker attach anodot-agent-my
elif [[ $1 == 'set-heap-size' ]]; then
  if [[ $2 =~ $num ]]; then
    echo "Please use only digits to set the heap size"
    exit 1
  fi
  sed -i '' -e "s/SDC_JAVA_OPTS_VALUE/${SDC_JAVA_OPTS} -Xmx$2m -Xms$2m -server/"
else
  echo "Wrong command supplied. Please use ./agent [install|run|rerun|attach]"
fi
