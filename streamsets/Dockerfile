FROM streamsets/datacollector

RUN "${SDC_DIST}/bin/streamsets" stagelibs -install="streamsets-datacollector-mongodb_3-lib,streamsets-datacollector-apache-kafka_2_0-lib"

VOLUME /data