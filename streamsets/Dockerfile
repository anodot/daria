FROM streamsets/datacollector:3.14

RUN MSQL_DRIVER_DIR=/opt/sdc-extras/streamsets-datacollector-jdbc-lib/lib/ \
        && MYSQL_CONNECTOR_VERSION=mysql-connector-java-8.0.18 \
        && sudo mkdir -p ${MSQL_DRIVER_DIR} \
        && sudo chown -R sdc:sdc /opt/sdc-extras \
        && wget https://cdn.mysql.com//Downloads/Connector-J/${MYSQL_CONNECTOR_VERSION}.tar.gz -O ${MSQL_DRIVER_DIR}/mysql_j.tar.gz \
        && tar -xzf ${MSQL_DRIVER_DIR}/mysql_j.tar.gz -C ${MSQL_DRIVER_DIR}\
        && mv ${MSQL_DRIVER_DIR}/${MYSQL_CONNECTOR_VERSION}/${MYSQL_CONNECTOR_VERSION}.jar ${MSQL_DRIVER_DIR}/${MYSQL_CONNECTOR_VERSION}.jar \
        && rm ${MSQL_DRIVER_DIR}/mysql_j.tar.gz && rm -rf ${MSQL_DRIVER_DIR}/${MYSQL_CONNECTOR_VERSION}

ENV SDC_CONF_PARSER_LIMIT=5048576 SDC_CONF_RUNNER_THREAD_POOL_SIZE="100" STREAMSETS_LIBRARIES_EXTRA_DIR="/opt/sdc-extras/" SDC_LOG="/data/logs"

COPY ./sdc-security.policy ${SDC_CONF}/sdc-security.policy
RUN "${SDC_DIST}/bin/streamsets" stagelibs -install="streamsets-datacollector-mongodb_3-lib,streamsets-datacollector-apache-kafka_2_0-lib,streamsets-datacollector-apache-kafka_0_11-lib,streamsets-datacollector-jdbc-lib,streamsets-datacollector-elasticsearch_5-lib"

VOLUME /data

# This build uses variable sasl.kerberos.domain.name
COPY ./kafka-clients-0.11.0.4-SNAPSHOT.jar ${SDC_DIST}/streamsets-libs/streamsets-datacollector-apache-kafka_0_11-lib/lib/kafka-clients-0.11.0.3.jar
COPY ./lib ${USER_LIBRARIES_DIR}