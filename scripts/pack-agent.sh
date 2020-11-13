AGENT_VERSION=$1 && \
docker pull anodot/daria:$AGENT_VERSION && \
docker pull anodot/streamsets:$AGENT_VERSION && \
docker save anodot/streamsets:$AGENT_VERSION anodot/daria:$AGENT_VERSION | gzip > agent.tar.gz
