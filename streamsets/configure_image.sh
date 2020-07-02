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
  "${SDC_DIST}/bin/streamsets" stagelibs -install="streamsets-datacollector-mongodb_3-lib,streamsets-datacollector-apache-kafka_2_0-lib,streamsets-datacollector-jdbc-lib,streamsets-datacollector-elasticsearch_5-lib,streamsets-datacollector-jython_2_7-lib"
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