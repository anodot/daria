if [[ $1 == 'install' ]]; then
  docker-compose pull && docker-compose up -d
elif [[ $1 == 'run' || $1 == 'rerun' ]]; then
    docker-compose up -d
elif [[ $1 == 'attach' ]]; then
  docker attach anodot-agent-my
else
  echo "Wrong command supplied. Please use ./agent [install|run|rerun|attach]"
fi
