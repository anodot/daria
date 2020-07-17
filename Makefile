NAP = 15
SLEEP = 60
THREADS = 4
DOCKER_COMPOSE_DEV_FILE = docker-compose-dev.yml
DOCKER_COMPOSE_DEV = docker-compose -f $(DOCKER_COMPOSE_DEV_FILE)
DOCKER_TEST = docker exec -i anodot-agent pytest -x  --disable-pytest-warnings
DOCKER_TEST_PARALLEL = $(DOCKER_TEST) -n $(THREADS) --dist=loadfile
DOCKER_TEST_DEV = $(DOCKER_TEST) -vv
DOCKER_TEST_DEV_PARALLEL = $(DOCKER_TEST_PARALLEL) -vv

##---------
## RELEASE
##---------
all: build-all test-all

build-all: get-streamsets-libs build sleep setup-elastic setup-kafka

test-all: test-antomation run-unit-tests test-destination test-api test-input test-pipelines

##-------------
## DEVELOPMENT
##-------------
all-dev: clean-docker-volumes build-all-dev sleep test-all-dev

build-all-dev: build-dev sleep setup-elastic setup-kafka

run-all-dev: clean-docker-volumes run-dev sleep setup-kafka setup-elastic

test-all-dev: run-unit-tests-dev test-dev-destination test-dev-api test-dev-condition-parser test-dev-input test-dev-pipelines

rerun: clean-docker-volumes run-base-services

rerun-agent:
	$(DOCKER_COMPOSE_DEV) restart agent

stop: clean-docker-volumes

##-----------------------
## TEST SEPARATE SOURCES
##-----------------------
test-directory: prepare-source test-destination-dev
	$(DOCKER_TEST_DEV) tests/test_input/test_directory_http.py
	$(DOCKER_TEST_DEV) tests/test_pipelines/test_directory_http.py

test-elastic: prepare-source build-elastic setup-elastic test-destination-dev
	$(DOCKER_TEST_DEV) tests/test_input/test_elastic_http.py
	$(DOCKER_TEST_DEV) tests/test_pipelines/test_elastic_http.py

test-influx: prepare-source build-influx test-destination-dev
	$(DOCKER_TEST_DEV) tests/test_input/test_influx_http.py
	$(DOCKER_TEST_DEV) tests/test_pipelines/test_influx_http.py

test-kafka: prepare-source build-kafka setup-kafka test-destination-dev
	$(DOCKER_TEST_DEV) tests/test_input/test_kafka_http.py
	$(DOCKER_TEST_DEV) tests/test_pipelines/test_kafka_http.py

test-mongo: prepare-source build-mongo test-destination-dev
	$(DOCKER_TEST_DEV) tests/test_input/test_mongo_http.py
	$(DOCKER_TEST_DEV) tests/test_pipelines/test_mongo_http.py

test-mysql: prepare-source build-mysql test-destination-dev
	$(DOCKER_TEST_DEV) tests/test_input/test_mysql_http.py
	$(DOCKER_TEST_DEV) tests/test_pipelines/test_mysql_http.py

test-postgres: prepare-source build-postgres test-destination-dev
	$(DOCKER_TEST_DEV) tests/test_input/test_postgres_http.py
	$(DOCKER_TEST_DEV) tests/test_pipelines/test_postgres_http.py

test-tcp: prepare-source test-destination-dev
	$(DOCKER_TEST_DEV) tests/test_input/test_tcp_http.py
	$(DOCKER_TEST_DEV) tests/test_pipelines/test_tcp_http.py

test-sage: prepare-source build-sage test-destination-dev
	$(DOCKER_TEST_DEV) tests/test_input/test_sage_http.py
	$(DOCKER_TEST_DEV) tests/test_pipelines/test_sage_http.py

test-destination-dev: prepare-source nap
	$(DOCKER_TEST_DEV) tests/test_destination.py

run-unit-tests-dev:
	$(DOCKER_TEST_DEV_PARALLEL) tests/unit/



##---------------------------
## RELEASE DEPENDENCY TARGETS
##---------------------------
build:
	docker-compose build --build-arg GIT_SHA1="$(shell git describe --dirty --always)"
	docker-compose up -d

test-antomation:
	$(DOCKER_TEST) tests/test_antomation.py

test-destination:
	$(DOCKER_TEST) tests/test_destination.py

test-input:
	$(DOCKER_TEST_PARALLEL) tests/test_input/

test-pipelines:
	$(DOCKER_TEST_PARALLEL) tests/test_pipelines/

test-api:
	$(DOCKER_TEST) tests/api/test_destination.py
	$(DOCKER_TEST) tests/api/source

run-unit-tests:
	$(DOCKER_TEST_PARALLEL) tests/unit/

get-streamsets-libs:
	rm -rf streamsets/lib/*
	curl -L https://github.com/anodot/anodot-sdc-stage/releases/download/v1.0.1/anodot-1.0.1.tar.gz -o /tmp/sdc.tar.gz && tar xvfz /tmp/sdc.tar.gz -C streamsets/lib
	pip install --upgrade pip && pip --isolated install --target streamsets/python-libs -r streamsets/python_requirements.txt

##-----------------------
## DEV DEPENDENCY TARGETS
##-----------------------
build-dev:
	$(DOCKER_COMPOSE_DEV) up -d --build
	docker exec -i anodot-agent python setup.py develop

run-dev:
	$(DOCKER_COMPOSE_DEV) up -d
	docker exec -i anodot-agent python setup.py develop

test-dev-destination:
	$(DOCKER_TEST_DEV) tests/test_destination.py

test-dev-condition-parser:
	$(DOCKER_TEST_DEV) tests/unit/test_condition_parser.py

test-dev-input:
	$(DOCKER_TEST_DEV_PARALLEL) tests/test_input/

test-dev-pipelines:
	$(DOCKER_TEST_DEV_PARALLEL) tests/test_pipelines/

test-dev-api:
	$(DOCKER_TEST_DEV) tests/api/test_destination.py
	$(DOCKER_TEST_DEV) tests/api/source

prepare-source: clean-docker-volumes run-base-services

clean-docker-volumes:
	rm -rf sdc-data
	rm -rf data
	$(DOCKER_COMPOSE_DEV) down -v

run-base-services:
	$(DOCKER_COMPOSE_DEV) up -d agent dc squid dummy_destination
	docker exec -i anodot-agent python setup.py develop

build-base-services: clean-docker-volumes
	$(DOCKER_COMPOSE_DEV) up -d --build agent dc squid dummy_destination
	docker exec -i anodot-agent python setup.py develop

build-elastic:
	$(DOCKER_COMPOSE_DEV) up -d es
	sleep $(SLEEP)

build-influx:
	$(DOCKER_COMPOSE_DEV) up -d influx

build-kafka: build-zookeeper
	$(DOCKER_COMPOSE_DEV) up -d kafka
	sleep $(SLEEP)

build-zookeeper:
	$(DOCKER_COMPOSE_DEV) up -d zookeeper

build-mongo:
	$(DOCKER_COMPOSE_DEV) up -d mongo

build-mysql:
	$(DOCKER_COMPOSE_DEV) up -d mysql

build-postgres:
	$(DOCKER_COMPOSE_DEV) up -d postgres

build-sage:
	docker-compose up -d --build sage

##--------------------------
## COMMON DEPENDENCY TARGETS
##--------------------------
setup-kafka:
	./upload-test-data-to-kafka.sh

setup-elastic:
	./upload-test-data-to-elastic.sh

sleep:
	sleep $(SLEEP)

nap:
	sleep $(NAP)
