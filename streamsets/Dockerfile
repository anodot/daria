FROM streamsets/datacollector:3.8.2

RUN "${SDC_DIST}/bin/streamsets" stagelibs -install="streamsets-datacollector-mongodb_3-lib,streamsets-datacollector-apache-kafka_2_0-lib"

VOLUME /data