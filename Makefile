NAP = 15
SLEEP = 60
DOCKER_COMPOSE_DEV = docker-compose-dev.yml
DOCKER_TEST = docker exec -i anodot-agent pytest -x
DOCKER_TEST_DEV = $(DOCKER_TEST) -vv

##------------
## RELEASE
##------------
all: build-all sleep test-all

##-------------
## DEVELOPMENT
##-------------
all-dev: clean-docker-volumes build-all-dev sleep test-all-dev

##-----------------------
## TEST SEPARATE SOURCES
##-----------------------
test-directory: prepare-source test-destination
	$(DOCKER_TEST_DEV) tests/test_pipelines/test_directory_http.py

test-elastic: prepare-source build-elastic setup-elastic test-destination
	$(DOCKER_TEST_DEV) tests/test_pipelines/test_elastic_http.py

test-influx: prepare-source build-influx test-destination
	$(DOCKER_TEST_DEV) tests/test_pipelines/test_influx_http.py

test-kafka: prepare-source build-kafka setup-kafka test-destination
	$(DOCKER_TEST_DEV) tests/test_pipelines/test_kafka_http.py

test-mongo: prepare-source build-mongo test-destination
	$(DOCKER_TEST_DEV) tests/test_pipelines/test_mongo_http.py

test-mysql: prepare-source build-mysql test-destination
	$(DOCKER_TEST_DEV) tests/test_pipelines/test_mysql_http.py

test-postgres: prepare-source build-postgres test-destination
	$(DOCKER_TEST_DEV) tests/test_pipelines/test_postgres_http.py

test-tcp: prepare-source test-destination
	$(DOCKER_TEST_DEV) tests/test_pipelines/test_tcp_http.py

test-destination: prepare-source nap
	$(DOCKER_TEST_DEV) tests/test_destination.py

##--------------------
## DEPENDENCY TARGETS
##--------------------
build-all: get-streamsets-stages
	docker-compose build --build-arg GIT_SHA1=$(git describe --dirty --always)
	docker-compose up -d

test-all: setup-elastic setup-kafka
	$(DOCKER_TEST)

build-all-dev:
	docker-compose -f $(DOCKER_COMPOSE_DEV) up -d --build
	docker exec -i anodot-agent python setup.py develop

test-all-dev: setup-elastic setup-kafka
	$(DOCKER_TEST_DEV)

prepare-source: clean-docker-volumes build-base-services

setup-kafka:
	./upload-test-data-to-kafka.sh

setup-elastic:
	./upload-test-data-to-elastic.sh

clean-docker-volumes:
	docker-compose down -v

build-base-services:
	docker-compose -f $(DOCKER_COMPOSE_DEV) up -d agent dc squid dummy_destination
	docker exec -i anodot-agent python setup.py develop

build-elastic:
	docker-compose up -d es
	sleep $(SLEEP)

build-influx:
	docker-compose up -d influx

build-kafka: build-zookeeper
	docker-compose up -d kafka
	sleep $(SLEEP)

build-zookeeper:
	docker-compose up -d zookeeper

build-mongo:
	docker-compose up -d mongo

build-mysql:
	docker-compose up -d mysql

build-postgres:
	docker-compose up -d postgres

get-streamsets-stages:
	curl -L https://github.com/anodot/anodot-sdc-stage/releases/download/v1.0.1/anodot-1.0.1.tar.gz -o /tmp/sdc.tar.gz && tar xvfz /tmp/sdc.tar.gz -C streamsets/lib

sleep:
	sleep $(SLEEP)

nap:
	sleep $(NAP)
