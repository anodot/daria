#!/usr/bin/env bash

set -e
set -u

function configure_sql_drivers() {
  local  MSQL_DRIVER_DIR=/opt/sdc-extras/streamsets-datacollector-jdbc-lib/lib/
  local  MYSQL_CONNECTOR_VERSION=8.0.18

  sudo mkdir -p ${MSQL_DRIVER_DIR}
  sudo chown -R sdc:sdc /opt/sdc-extras
  wget https://repo1.maven.org/maven2/mysql/mysql-connector-java/${MYSQL_CONNECTOR_VERSION}/mysql-connector-java-${MYSQL_CONNECTOR_VERSION}.jar -O ${MSQL_DRIVER_DIR}/${MYSQL_CONNECTOR_VERSION}.jar
  unzip -l -q ${MSQL_DRIVER_DIR}/${MYSQL_CONNECTOR_VERSION}.jar
}

function install_stage_libs() {
  "${SDC_DIST}/bin/streamsets" stagelibs -install="streamsets-datacollector-mongodb_3-lib,streamsets-datacollector-jdbc-lib,streamsets-datacollector-elasticsearch_5-lib,streamsets-datacollector-jython_2_7-lib,streamsets-datacollector-apache-kafka_2_0-lib"

  # update kafka libraries
  local KAFKA_TMP_DIR=/tmp/streamsets-datacollector-3.21.0/streamsets-libs/streamsets-datacollector-apache-kafka_2_2-lib/lib
  local KAFKA_SDC_DIR=${SDC_DIST}/streamsets-libs/streamsets-datacollector-apache-kafka_2_0-lib/lib

  rm ${KAFKA_SDC_DIR}/lz4-java-1.4.1.jar ${KAFKA_SDC_DIR}/snappy-0.4.jar
  wget https://repo1.maven.org/maven2/org/lz4/lz4-java/1.5.0/lz4-java-1.5.0.jar -O ${KAFKA_SDC_DIR}/lz4-java-1.5.0.jar
  wget https://repo1.maven.org/maven2/com/github/luben/zstd-jni/1.3.8-1/zstd-jni-1.3.8-1.jar -O ${KAFKA_SDC_DIR}/zstd-jni-1.3.8-1.jar
  wget https://repo1.maven.org/maven2/org/xerial/snappy/snappy-java/1.1.7.2/snappy-java-1.1.7.2.jar -O ${KAFKA_SDC_DIR}/snappy-java-1.1.7.2.jar
}

function make_sdc_copy() {
    sudo cp -frv "${SDC_CONF}" /opt/sdc_conf
}

function set_permissions() {
    sudo chown -R sdc:sdc /opt/sdc_conf
    sudo chown -R sdc:sdc /custom_entrypoint.sh
    sudo chmod +x /custom_entrypoint.sh
}

############################################### execution start here #################################################
configure_sql_drivers
install_stage_libs
make_sdc_copy
set_permissions