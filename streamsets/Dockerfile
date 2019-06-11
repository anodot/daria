FROM streamsets/datacollector:3.8.2

RUN "${SDC_DIST}/bin/streamsets" stagelibs -install="streamsets-datacollector-mongodb_3-lib,streamsets-datacollector-apache-kafka_2_0-lib"

ENV SDC_CONF_PARSER_LIMIT=5048576 SDC_CONF_RUNNER_THREAD_POOL_SIZE="100"
VOLUME /data