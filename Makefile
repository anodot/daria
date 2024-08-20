NAP = 15
SLEEP = 60
THREADS = 2
DOCKER_COMPOSE_DEV_FILE = docker-compose-dev.yml
DOCKER_COMPOSE_DEV = docker compose -f $(DOCKER_COMPOSE_DEV_FILE)
DOCKER_TEST = docker exec -i anodot-agent pytest -x -vv --disable-pytest-warnings
DOCKER_TEST_PARALLEL = $(DOCKER_TEST) -n $(THREADS) --dist=loadfile

##---------
## RELEASE
##---------
all: build-all test-general test-pipelines-1 test-pipelines-2

build-all: get-streamsets-libs build-docker

test-all: test-general test-pipelines-1 test-pipelines-2

test-general: run-base-services run-unit-tests test-sdc-client test-flask-app test-streamsets run-general-test-services test-raw-input test-raw-pipelines test-destination test-run-test-pipeline test-apply test-api test-api-scripts test-export-sources test-streamsets-2 test-send-to-bc test-monitoring-metrics

test-pipelines-1: bootstrap-test-pipelines run-services-for-test-1
	$(DOCKER_TEST_PARALLEL) tests/test_input/test_1
	$(DOCKER_TEST_PARALLEL) tests/test_pipelines/test_1

test-pipelines-2: bootstrap-test-pipelines run-services-for-test-2
	$(DOCKER_TEST_PARALLEL) tests/test_input/test_2
	$(DOCKER_TEST_PARALLEL) tests/test_pipelines/test_2

bootstrap-test-pipelines: run-base-services test-streamsets test-destination
	docker exec -i dc bash -c '$$SDC_DIST/bin/streamsets stagelib-cli jks-credentialstore add -i jks -n testmongopass -c root'
	docker exec -i dc2 bash -c '$$SDC_DIST/bin/streamsets stagelib-cli jks-credentialstore add -i jks -n testmongopass -c root'

run-services-for-test-1: _run-services-for-test-1 half-sleep setup-victoria setup-kafka
_run-services-for-test-1:
	docker compose up -d mongo zookeeper kafka influx influx-2 postgres victoriametrics

run-services-for-test-2: _run-services-for-test-2 sleep setup-elastic setup-zabbix
_run-services-for-test-2:
	docker compose up -d mysql es zabbix-server zabbix-web zabbix-agent clickhouse snmpsim sage

run-base-services:
	docker compose up -d agent dc dc2 squid dummy_destination
	sleep 60

run-general-test-services: _run-general-test-services sleep setup-elastic setup-kafka
_run-general-test-services:
	docker compose up -d es influx mongo sage mysql snmpsim kafka

##-------------
## DEVELOPMENT
##-------------
all-dev: clean-docker-volumes build-all-dev sleep test-all

build-all-dev: build-dev sleep setup-all

run-all-dev: clean-docker-volumes run-dev sleep setup-all

rerun: bootstrap

rerun-agent:
	$(DOCKER_COMPOSE_DEV) restart agent

stop: clean-docker-volumes

##-----------------------
## TEST SEPARATE SOURCES
##-----------------------
test-directory: bootstrap
	$(DOCKER_TEST) tests/test_input/test_1/test_directory_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_1/test_directory_http.py

test-prtg: bootstrap
	$(DOCKER_TEST) tests/test_input/test_1/test_prtg.py
	$(DOCKER_TEST) tests/test_pipelines/test_1/test_prtg.py

test-elastic: bootstrap run-elastic setup-elastic
	$(DOCKER_TEST) tests/test_input/test_2/test_elastic_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_2/test_elastic_http.py

test-promql: bootstrap run-victoria
	$(DOCKER_TEST) tests/test_input/test_1/test_promql_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_1/test_promql_http.py

test-influx: bootstrap run-influx run-influx-2 nap
	$(DOCKER_TEST) tests/test_input/test_1/test_influx_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_1/test_influx_http.py

test-kafka: bootstrap run-kafka
	$(DOCKER_TEST) tests/test_input/test_1/test_kafka_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_1/test_kafka_http.py

test-mongo: bootstrap run-mongo
	docker exec -i dc bash -c '$$SDC_DIST/bin/streamsets stagelib-cli jks-credentialstore add -i jks -n testmongopass -c root'
	$(DOCKER_TEST) tests/test_input/test_1/test_mongo_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_1/test_mongo_http.py

test-mysql: bootstrap run-mysql sleep
	$(DOCKER_TEST) tests/test_input/test_2/test_mysql_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_2/test_mysql_http.py

test-postgres: bootstrap run-postgres sleep
	$(DOCKER_TEST) tests/test_input/test_1/test_postgres_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_1/test_postgres_http.py

test-clickhouse: bootstrap run-clickhouse sleep
	$(DOCKER_TEST) tests/test_input/test_2/test_clickhouse.py
	$(DOCKER_TEST) tests/test_pipelines/test_2/test_clickhouse.py

test-tcp: bootstrap
	$(DOCKER_TEST) tests/test_input/test_1/test_tcp_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_1/test_tcp_http.py

test-sage: bootstrap run-sage
	$(DOCKER_TEST) tests/test_input/test_2/test_sage_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_2/test_sage_http.py

test-zabbix: bootstrap run-zabbix
	$(DOCKER_TEST) tests/test_input/test_2/test_zabbix_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_2/test_zabbix_http.py

test-cacti: bootstrap run-mysql half-sleep
	$(DOCKER_TEST) tests/test_input/test_2/test_cacti.py
	$(DOCKER_TEST) tests/test_pipelines/test_2/test_cacti.py

test-oracle: bootstrap
	$(DOCKER_TEST) tests/test_input/test_2/test_oracle.py

test-observium: bootstrap run-mysql half-sleep
	$(DOCKER_TEST) tests/test_input/test_2/test_observium.py
	$(DOCKER_TEST) tests/test_pipelines/test_2/test_observium.py

test-mssql: bootstrap
	docker exec -i dc bash -c '$$SDC_DIST/bin/streamsets stagelib-cli jks-credentialstore add -i jks -n testmssql -c UserTest123$$'
	$(DOCKER_TEST) tests/test_input/test_1/test_mssql.py

test-databricks: bootstrap
	$(DOCKER_TEST) tests/test_input/test_1/test_databricks.py

test-actian: bootstrap
	$(DOCKER_TEST) tests/test_input/test_2/test_actian.py

test-snmp: bootstrap run-snmpsim
	$(DOCKER_TEST) tests/test_input/test_2/test_snmp.py
	$(DOCKER_TEST) tests/test_pipelines/test_2/test_snmp.py

##---------------------------
## RELEASE DEPENDENCY TARGETS
##---------------------------
build-docker:
	docker compose down -v
	docker compose build --build-arg GIT_SHA1="$(git describe --tags --dirty --always)"

run-all:
	docker compose up -d

test-apply:
	$(DOCKER_TEST) tests/test_apply.py

test-send-to-bc:
	$(DOCKER_TEST) tests/test_send_to_bc.py

test-destination:
	$(DOCKER_TEST) tests/test_destination.py

test-streamsets:
	$(DOCKER_TEST) tests/test_streamsets.py

test-raw-input:
	$(DOCKER_TEST_PARALLEL) tests/test_raw/test_input

test-raw-pipelines:
	$(DOCKER_TEST_PARALLEL) tests/test_raw/test_pipelines

test-streamsets-2:
	$(DOCKER_TEST) tests/test_streamsets_with_preferred_type.py
	$(DOCKER_TEST) tests/test_streamsets_2.py

test-input:
	$(DOCKER_TEST_PARALLEL) tests/test_input/

test-export-sources:
	$(DOCKER_TEST_PARALLEL) tests/test_export_sources.py

test-run-test-pipeline:
	$(DOCKER_TEST) tests/test_run_test_pipeline.py

test-monitoring-metrics:
	$(DOCKER_TEST) tests/test_monitoring.py

test-api:
	$(DOCKER_TEST) tests/api/test_destination.py
	$(DOCKER_TEST) tests/api/test_streamsets.py
	$(DOCKER_TEST) tests/api/source
	$(DOCKER_TEST) tests/api/pipeline

test-api-scripts:
	$(DOCKER_TEST) tests/api/test_scripts.py

test-flask-app:
	$(DOCKER_TEST) tests/api/test_flask_app.py

test-sdc-client:
	$(DOCKER_TEST) tests/test_sdc_client

run-unit-tests:
	$(DOCKER_TEST_PARALLEL) tests/unit/

get-streamsets-libs: install-streamsets-requirements
	rm -rf containers/streamsets/lib/anodot
	curl -L https://github.com/anodot/anodot-sdc-stage/releases/download/v2.0.7/anodot-2.0.7.tar.gz -o /tmp/sdc.tar.gz && tar xvfz /tmp/sdc.tar.gz -C containers/streamsets/lib

install-streamsets-requirements:
	rm -rf containers/streamsets/python-libs/*
	pip install --upgrade pip && pip install --target containers/streamsets/python-libs -r containers/streamsets/python_requirements.txt

setup-all: setup-victoria setup-kafka setup-elastic setup-zabbix

##-----------------------
## DEV DEPENDENCY TARGETS
##-----------------------
build-dev:
	$(DOCKER_COMPOSE_DEV) up -d --build

run-dev:
	$(DOCKER_COMPOSE_DEV) up -d

bootstrap: clean-docker-volumes run-base-services-dev test-streamsets test-destination

clean-docker-volumes:
	rm -rf sdc-data/*
	rm -rf sdc-data2/*
	rm -rf agent/output/*
	$(DOCKER_COMPOSE_DEV) down -v --remove-orphans


run-base-services-dev: _run-base-services-dev sleep

_run-base-services-dev:
	$(DOCKER_COMPOSE_DEV) up -d agent dc squid dummy_destination
	#docker exec -i anodot-agent python setup.py develop

build-base-services: clean-docker-volumes _build-base-services nap

_build-base-services:
	$(DOCKER_COMPOSE_DEV) up -d --build agent dc squid dummy_destination
	docker exec -i anodot-agent python setup.py develop

run-dc2:
	$(DOCKER_COMPOSE_DEV) up -d dc2

run-elastic: _run-elastic sleep setup-elastic

_run-elastic:
	$(DOCKER_COMPOSE_DEV) up -d es

run-influx:
	$(DOCKER_COMPOSE_DEV) up -d influx

run-influx-2:
	$(DOCKER_COMPOSE_DEV) up -d influx-2

run-snmpsim:
	$(DOCKER_COMPOSE_DEV) up -d snmpsim

run-victoria: _run-victoria nap setup-victoria

_run-victoria:
	$(DOCKER_COMPOSE_DEV) up -d victoriametrics

run-kafka: run-zookeeper _run-kafka setup-kafka

_run-kafka:
	$(DOCKER_COMPOSE_DEV) up -d kafka
	sleep 15

run-zookeeper:
	$(DOCKER_COMPOSE_DEV) up -d zookeeper

run-mongo:
	$(DOCKER_COMPOSE_DEV) up -d mongo

run-cacti: run-mysql

run-mysql:
	$(DOCKER_COMPOSE_DEV) up -d mysql

run-observium: run-mysql

run-postgres:
	$(DOCKER_COMPOSE_DEV) up -d postgres

run-clickhouse:
	$(DOCKER_COMPOSE_DEV) up -d clickhouse

run-sage:
	$(DOCKER_COMPOSE_DEV) up -d --build sage

run-zabbix: _run-zabbix sleep setup-zabbix

_run-zabbix:
	$(DOCKER_COMPOSE_DEV) up -d mysql zabbix-server zabbix-web zabbix-agent

##--------------------------
## COMMON DEPENDENCY TARGETS
##--------------------------
setup-kafka:
	./scripts/upload-test-data-to-kafka.sh

setup-elastic:
	sleep 30
	./scripts/upload-test-data-to-elastic.sh

setup-victoria:
	./scripts/upload-test-data-to-victoria.sh

setup-zabbix:
	docker cp ./scripts/upload-test-data-to-zabbix.py anodot-agent:/tmp/
	docker exec anodot-agent python /tmp/upload-test-data-to-zabbix.py

setup-pre-commit:
	pip install pre-commit
	pre-commit install

sleep:
	sleep $(SLEEP)

half-sleep:
	sleep 30

nap:
	sleep $(NAP)

show-all-logs:
	docker logs anodot-agent;
	echo "DC logs "; docker logs dc;
	echo "DC 2 logs"; docker logs dc2;
	echo "Dummy logs"; docker logs dummy_destination;
	echo "Agent logs"; docker exec -i anodot-agent cat /var/log/agent/agent.log;
