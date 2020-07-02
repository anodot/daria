FROM streamsets/datacollector:3.15.0

ENV SDC_CONF_PARSER_LIMIT=5048576 SDC_CONF_RUNNER_THREAD_POOL_SIZE="100" STREAMSETS_LIBRARIES_EXTRA_DIR="/opt/sdc-extras/" SDC_LOG="/data/logs"
COPY ./sdc-security.policy ${SDC_CONF}/sdc-security.policy

COPY ./lib ${USER_LIBRARIES_DIR}
COPY ./configure_image.sh /tmp/configure_image.sh
COPY ./custom_entrypoint.sh /

RUN sudo chmod +x /tmp/configure_image.sh && /tmp/configure_image.sh

# This build uses variable sasl.kerberos.domain.name
COPY ./kafka-clients-2.0.2-SNAPSHOT.jar ${SDC_DIST}/streamsets-libs/streamsets-datacollector-apache-kafka_2_0-lib/lib/kafka-clients-2.0.1.jar

COPY python-libs ${SDC_DIST}/python-libs

VOLUME /data

ENTRYPOINT ["/custom_entrypoint.sh"]
CMD ["dc", "-exec"]