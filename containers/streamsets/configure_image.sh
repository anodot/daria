#!/usr/bin/env bash

set -e
set -u

function configure_sql_drivers() {
  local  JDBC_DRIVER_DIR=/opt/sdc-extras/streamsets-datacollector-jdbc-lib/lib/
  local  MYSQL_CONNECTOR_VERSION=8.0.18
  local  CLICKHOUSE_DRIVER_VERSION=0.3.0
  local  ORACLE_DRIVER_VERSION=19.11.0.0

  sudo mkdir -p ${JDBC_DRIVER_DIR}
  sudo chown -R sdc:sdc /opt/sdc-extras
  wget https://repo1.maven.org/maven2/mysql/mysql-connector-java/${MYSQL_CONNECTOR_VERSION}/mysql-connector-java-${MYSQL_CONNECTOR_VERSION}.jar -O ${JDBC_DRIVER_DIR}/${MYSQL_CONNECTOR_VERSION}.jar
  wget https://repo1.maven.org/maven2/com/oracle/database/jdbc/ojdbc8/${ORACLE_DRIVER_VERSION}/ojdbc8-${ORACLE_DRIVER_VERSION}.jar -O ${JDBC_DRIVER_DIR}/${ORACLE_DRIVER_VERSION}.jar

  # clickhouse dependencies
  wget https://repo1.maven.org/maven2/ru/yandex/clickhouse/clickhouse-jdbc/${CLICKHOUSE_DRIVER_VERSION}/clickhouse-jdbc-${CLICKHOUSE_DRIVER_VERSION}.jar -O ${JDBC_DRIVER_DIR}/clickhouse-jdbc-${CLICKHOUSE_DRIVER_VERSION}.jar
  wget https://repo1.maven.org/maven2/org/apache/httpcomponents/httpclient/4.5.13/httpclient-4.5.13.jar -O ${JDBC_DRIVER_DIR}/httpclient-4.5.13.jar
  wget https://repo1.maven.org/maven2/org/apache/httpcomponents/httpmime/4.5.13/httpmime-4.5.13.jar -O ${JDBC_DRIVER_DIR}/httpmime-4.5.13.jar
  wget https://repo1.maven.org/maven2/com/fasterxml/jackson/core/jackson-databind/2.9.10.8/jackson-databind-2.9.10.8.jar -O ${JDBC_DRIVER_DIR}/jackson-databind-2.9.10.8.jar
  wget https://repo1.maven.org/maven2/com/fasterxml/jackson/core/jackson-core/2.9.10/jackson-core-2.9.10.jar -O ${JDBC_DRIVER_DIR}/jackson-core-2.9.10.jar
  wget https://repo1.maven.org/maven2/org/lz4/lz4-java/1.7.1/lz4-java-1.7.1.jar -O ${JDBC_DRIVER_DIR}/lz4-java-1.7.1.jar
  wget https://repo1.maven.org/maven2/org/slf4j/slf4j-api/1.7.30/slf4j-api-1.7.30.jar -O ${JDBC_DRIVER_DIR}/slf4j-api-1.7.30.jar
  wget https://repo1.maven.org/maven2/org/apache/httpcomponents/httpcore/4.4.13/httpcore-4.4.13.jar -O ${JDBC_DRIVER_DIR}/httpcore-4.4.13.jar
  wget https://repo1.maven.org/maven2/commons-logging/commons-logging/1.2/commons-logging-1.2.jar -O ${JDBC_DRIVER_DIR}/commons-logging-1.2.jar

  # databricks
  local SIMBA_DRIVER_VERSION=2.6.21.1039
  wget https://databricks-bi-artifacts.s3.us-east-2.amazonaws.com/simbaspark-drivers/jdbc/2.6.21/SimbaSparkJDBC42-${SIMBA_DRIVER_VERSION}.zip \
                      -O ${JDBC_DRIVER_DIR}/SimbaSparkJDBC42-${SIMBA_DRIVER_VERSION}.zip
  #wget https://databricks-bi-artifacts.s3.us-east-2.amazonaws.com/simbaspark-drivers/jdbc/${SIMBA_DRIVER_VERSION}/SimbaSparkJDBC42-${SIMBA_DRIVER_VERSION}.1030.zip \
  #                   -O ${JDBC_DRIVER_DIR}/SimbaSparkJDBC42-${SIMBA_DRIVER_VERSION}.1030.zip
  unzip ${JDBC_DRIVER_DIR}/SimbaSparkJDBC42-${SIMBA_DRIVER_VERSION}.zip -d ${JDBC_DRIVER_DIR}
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
