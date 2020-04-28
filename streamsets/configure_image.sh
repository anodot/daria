#!/usr/bin/env bash

set -e
set -u

function configure_sql_drivers() {
  local  MSQL_DRIVER_DIR=/opt/sdc-extras/streamsets-datacollector-jdbc-lib/lib/
  local  MYSQL_CONNECTOR_VERSION=mysql-connector-java-8.0.18

  sudo mkdir -p ${MSQL_DRIVER_DIR}
  sudo chown -R sdc:sdc /opt/sdc-extras
  wget https://cdn.mysql.com//Downloads/Connector-J/${MYSQL_CONNECTOR_VERSION}.tar.gz -O ${MSQL_DRIVER_DIR}/mysql_j.tar.gz

  tar -xzf ${MSQL_DRIVER_DIR}/mysql_j.tar.gz -C ${MSQL_DRIVER_DIR}
  mv ${MSQL_DRIVER_DIR}/${MYSQL_CONNECTOR_VERSION}/${MYSQL_CONNECTOR_VERSION}.jar ${MSQL_DRIVER_DIR}/${MYSQL_CONNECTOR_VERSION}.jar
  rm -rf ${MSQL_DRIVER_DIR}/mysql_j.tar.gz
  rm -rf ${MSQL_DRIVER_DIR}/${MYSQL_CONNECTOR_VERSION}
}

function install_stage_libs() {
  "${SDC_DIST}/bin/streamsets" stagelibs -install="streamsets-datacollector-mongodb_3-lib,streamsets-datacollector-apache-kafka_2_0-lib,streamsets-datacollector-jdbc-lib,streamsets-datacollector-elasticsearch_5-lib"
}

############################################### execution start here #################################################
configure_sql_drivers
install_stage_libs
