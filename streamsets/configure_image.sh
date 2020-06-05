#!/usr/bin/env bash

set -e
set -u

function configure_sql_drivers() {
  local JDBC_DRIVER_DIR=/opt/sdc-extras/streamsets-datacollector-jdbc-lib/lib/
  local MYSQL_CONNECTOR_VERSION=8.0.18
  local IVY_VERSION=2.3.0

  sudo mkdir -p ${JDBC_DRIVER_DIR}
  sudo chown -R sdc:sdc /opt/sdc-extras
  wget https://repo1.maven.org/maven2/mysql/mysql-connector-java/${MYSQL_CONNECTOR_VERSION}/mysql-connector-java-${MYSQL_CONNECTOR_VERSION}.jar -O ${JDBC_DRIVER_DIR}/${MYSQL_CONNECTOR_VERSION}.jar
  unzip -l -q ${JDBC_DRIVER_DIR}/${MYSQL_CONNECTOR_VERSION}.jar

  curl -L http://search.maven.org/remotecontent?filepath=org/apache/ivy/ivy/${IVY_VERSION}/ivy-${IVY_VERSION}.jar -o /tmp/ivy-${IVY_VERSION}.jar
  echo '<ivysettings>
    <settings defaultResolver="chain"/>
    <resolvers>
        <chain name="chain">
            <ibiblio name="central" m2compatible="true"/>
            <ibiblio name="maven-https" m2compatible="true" root="https://repo1.maven.org/maven2/"/>
        </chain>
    </resolvers>
</ivysettings>' >> /tmp/ivysettings.xml
  java -jar /tmp/ivy-${IVY_VERSION}.jar -settings /tmp/ivysettings.xml -dependency org.apache.hive hive-jdbc 3.1.2 -retrieve "${JDBC_DRIVER_DIR}/[artifact]-[revision](-[classifier]).[ext]"
}

function install_stage_libs() {
  "${SDC_DIST}/bin/streamsets" stagelibs -install="streamsets-datacollector-mongodb_3-lib,streamsets-datacollector-apache-kafka_2_0-lib,streamsets-datacollector-jdbc-lib,streamsets-datacollector-elasticsearch_5-lib"
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