NAP = 15
SLEEP = 60
THREADS = 8
DOCKER_COMPOSE_DEV_FILE = docker-compose-dev.yml
DOCKER_COMPOSE_DEV = docker-compose -f $(DOCKER_COMPOSE_DEV_FILE)
DOCKER_TEST = docker exec -i anodot-agent pytest -x -vv --disable-pytest-warnings
DOCKER_TEST_PARALLEL = $(DOCKER_TEST) -n $(THREADS) --dist=loadfile

##---------
## RELEASE
##---------
all: build-all test-all

build-all: get-streamsets-libs build-docker sleep setup-all

test-all: run-unit-tests test-flask-app test-streamsets test-raw-input test-raw-pipelines test-destination test-run-test-pipeline test-apply test-api test-api-scripts test-input test-export-sources test-streamsets-2 test-send-to-bc test-pipelines test-send-to-watermark

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
	$(DOCKER_TEST) tests/test_input/test_directory_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_directory_http.py

test-elastic: bootstrap run-elastic setup-elastic
	$(DOCKER_TEST) tests/test_input/test_elastic_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_elastic_http.py

test-promql: bootstrap run-victoria nap setup-victoria
	$(DOCKER_TEST) tests/test_input/test_promql_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_promql_http.py

test-influx: bootstrap run-influx nap
	$(DOCKER_TEST) tests/test_input/test_influx_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_influx_http.py

test-kafka: bootstrap run-kafka setup-kafka
	$(DOCKER_TEST) tests/test_input/test_kafka_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_kafka_http.py

test-mongo: bootstrap run-mongo
	docker exec -i dc bash -c '$$SDC_DIST/bin/streamsets stagelib-cli jks-credentialstore add -i jks -n testmongopass -c root'
	$(DOCKER_TEST) tests/test_input/test_mongo_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_mongo_http.py

test-mysql: bootstrap run-mysql sleep
	$(DOCKER_TEST) tests/test_input/test_mysql_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_mysql_http.py

test-postgres: bootstrap run-postgres sleep
	$(DOCKER_TEST) tests/test_input/test_postgres_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_postgres_http.py

test-clickhouse: bootstrap run-clickhouse sleep
	$(DOCKER_TEST) tests/test_input/test_clickhouse.py
	$(DOCKER_TEST) tests/test_pipelines/test_clickhouse.py

test-tcp: bootstrap
	$(DOCKER_TEST) tests/test_input/test_tcp_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_tcp_http.py

test-sage: bootstrap run-sage
	$(DOCKER_TEST) tests/test_input/test_sage_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_sage_http.py

test-zabbix: bootstrap run-zabbix
	$(DOCKER_TEST) tests/test_input/test_zabbix_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_zabbix_http.py

test-cacti: bootstrap run-mysql sleep
	$(DOCKER_TEST) tests/test_input/test_cacti.py
	$(DOCKER_TEST) tests/test_pipelines/test_cacti.py

test-oracle: bootstrap
	$(DOCKER_TEST) tests/test_input/test_2/test_oracle.py

test-mssql:
	docker exec -i dc bash -c '$$SDC_DIST/bin/streamsets stagelib-cli jks-credentialstore add -i jks -n testmssql -c UserTest123$$'
	$(DOCKER_TEST) tests/test_input/test_mssql.py

test-databricks: bootstrap
	$(DOCKER_TEST) tests/test_input/test_2/test_databricks.py

##---------------------------
## RELEASE DEPENDENCY TARGETS
##---------------------------
build-docker:
	docker-compose down -v
	docker-compose build --build-arg GIT_SHA1="$(git describe --tags --dirty --always)"
	docker-compose up -d

test-apply:
	$(DOCKER_TEST) tests/test_apply.py

test-send-to-bc:
	$(DOCKER_TEST) tests/test_send_to_bc.py

test-send-to-watermark:
	$(DOCKER_TEST) tests/test_send_watermark.py

test-destination:
	$(DOCKER_TEST) tests/test_destination.py

test-streamsets:
	$(DOCKER_TEST) tests/test_streamsets.py

test-raw-input:
	$(DOCKER_TEST_PARALLEL) tests/test_raw/test_input

test-raw-pipelines:
	$(DOCKER_TEST_PARALLEL) tests/test_raw/test_pipelines

test-streamsets-2:
	$(DOCKER_TEST) tests/test_streamsets_2.py

test-input:
	$(DOCKER_TEST_PARALLEL) tests/test_input/

test-export-sources:
	$(DOCKER_TEST_PARALLEL) tests/test_export_sources.py

test-pipelines:
	docker exec -i dc bash -c '$$SDC_DIST/bin/streamsets stagelib-cli jks-credentialstore add -i jks -n testmongopass -c root'
	docker exec -i dc2 bash -c '$$SDC_DIST/bin/streamsets stagelib-cli jks-credentialstore add -i jks -n testmongopass -c root'
	sleep 15
	$(DOCKER_TEST_PARALLEL) tests/test_pipelines/

test-run-test-pipeline:
	$(DOCKER_TEST) tests/test_run_test_pipeline.py

test-api:
	$(DOCKER_TEST) tests/api/test_destination.py
	$(DOCKER_TEST) tests/api/test_streamsets.py
	$(DOCKER_TEST) tests/api/source
	$(DOCKER_TEST) tests/api/pipeline

test-api-scripts:
	$(DOCKER_TEST) tests/api/test_scripts.py

test-flask-app:
	$(DOCKER_TEST) tests/api/test_flask_app.py

run-unit-tests:
	$(DOCKER_TEST_PARALLEL) tests/unit/

get-streamsets-libs: install-streamsets-requirements
	rm -rf containers/streamsets/lib/anodot
	curl -L https://github.com/anodot/anodot-sdc-stage/releases/download/v2.0.4/anodot-2.0.4.tar.gz -o /tmp/sdc.tar.gz && tar xvfz /tmp/sdc.tar.gz -C containers/streamsets/lib

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

bootstrap: clean-docker-volumes run-base-services test-streamsets test-destination

clean-docker-volumes:
	rm -rf sdc-data
	rm -rf sdc-data2
	rm -rf agent/output
	$(DOCKER_COMPOSE_DEV) down -v --remove-orphans

run-base-services: _run-base-services sleep

_run-base-services:
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

run-kafka: run-zookeeper _run-kafka sleep setup-kafka

_run-kafka:
	$(DOCKER_COMPOSE_DEV) up -d kafka

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

setup-elastic: half-sleep
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
