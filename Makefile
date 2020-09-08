NAP = 20
SLEEP = 60
THREADS = 6
DOCKER_COMPOSE_DEV_FILE = docker-compose-dev.yml
DOCKER_COMPOSE_DEV = docker-compose -f $(DOCKER_COMPOSE_DEV_FILE)
DOCKER_TEST = docker exec -i anodot-agent pytest -x -vv --disable-pytest-warnings
DOCKER_TEST_PARALLEL = $(DOCKER_TEST) -n $(THREADS) --dist=loadfile

##---------
## RELEASE
##---------
all: build-all test-all

build-all: get-streamsets-libs build-docker run-base nap

test-all: run-unit-tests test-flask-app test-destination first-step second-step test-antomation test-api-scripts

##-------------
## DEVELOPMENT
##-------------
all-dev: clean-docker-volumes build-all-dev sleep test-all

build-all-dev: build-dev sleep setup-elastic setup-kafka setup-victoria

run-all-dev: clean-docker-volumes run-dev sleep setup-kafka setup-elastic

rerun: bootstrap

rerun-agent:
	$(DOCKER_COMPOSE_DEV) restart agent

stop: clean-docker-volumes

##-----------------------
## TEST SEPARATE SOURCES
##-----------------------
test-directory: bootstrap nap test-destination
	$(DOCKER_TEST) tests/test_input/test_directory_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_directory_http.py

test-elastic: bootstrap run-elastic setup-elastic test-destination
	$(DOCKER_TEST) tests/test_input/test_elastic_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_elastic_http.py

test-victoria: bootstrap run-victoria nap setup-victoria test-destination
	$(DOCKER_TEST) tests/test_input/test_victoria_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_victoria_http.py

test-influx: bootstrap run-influx nap test-destination
	$(DOCKER_TEST) tests/test_input/test_influx_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_influx_http.py

test-kafka: bootstrap run-kafka setup-kafka test-destination
	$(DOCKER_TEST) tests/test_input/test_kafka_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_kafka_http.py

test-mongo: bootstrap run-mongo nap test-destination
	$(DOCKER_TEST) tests/test_input/test_mongo_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_mongo_http.py

test-mysql: bootstrap run-mysql nap test-destination
	$(DOCKER_TEST) tests/test_input/test_mysql_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_mysql_http.py

test-postgres: bootstrap run-postgres nap test-destination
	$(DOCKER_TEST) tests/test_input/test_postgres_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_postgres_http.py

test-tcp: bootstrap nap test-destination
	$(DOCKER_TEST) tests/test_input/test_tcp_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_tcp_http.py

test-sage: bootstrap run-sage nap test-destination
	$(DOCKER_TEST) tests/test_input/test_sage_http.py
	$(DOCKER_TEST) tests/test_pipelines/test_sage_http.py



##---------------------------
## RELEASE DEPENDENCY TARGETS
##---------------------------
build-docker:
	docker-compose build --build-arg GIT_SHA1="$(shell git describe --dirty --always)"

first-step: run-first-half test-api-first-half test-input-first-half test-pipelines-first-half stop-first-half

second-step: run-second-half test-api-second-half test-input-second-half test-pipelines-second-half

run-first-half: run-elastic run-mongo run-victoria run-influx sleep setup-elastic setup-victoria

test-api-first-half:
	$(DOCKER_TEST) tests/api/test_destination.py
	$(DOCKER_TEST) tests/api/source/test_elastic.py tests/api/source/test_influx.py tests/api/source/test_mongo.py
	$(DOCKER_TEST) tests/api/pipeline/test_influx.py

test-input-first-half:
	$(DOCKER_TEST_PARALLEL) tests/test_input/test_elastic_http.py tests/test_input/test_mongo_http.py tests/test_input/test_victoria_http.py tests/test_input/test_influx_http.py tests/test_input/test_tcp_http.py

test-pipelines-first-half:
	$(DOCKER_TEST_PARALLEL) tests/test_pipelines/test_elastic_http.py tests/test_pipelines/test_influx_http.py tests/test_pipelines/test_kafka_http.py tests/test_pipelines/test_mongo_http.py tests/test_pipelines/test_victoria_http.py

run-second-half: run-mysql run-postgres run-sage run-kafka nap setup-kafka

stop-first-half:
	docker-compose stop es influx mongo victoria

test-input-second-half:
	$(DOCKER_TEST_PARALLEL) tests/test_input/test_mysql_http.py tests/test_input/test_postgres_http.py tests/test_input/test_kafka_http.py tests/test_input/test_sage_http.py tests/test_input/test_directory_http.py

test-pipelines-second-half:
	$(DOCKER_TEST_PARALLEL) tests/test_pipelines/test_mysql_http.py tests/test_pipelines/test_postgres_http.py tests/test_pipelines/test_sage_http.py tests/test_pipelines/test_directory_http.py tests/test_pipelines/test_tcp_http.py

test-api-second-half:
	$(DOCKER_TEST) tests/api/source

test-antomation: run-mongo
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
	$(DOCKER_TEST) tests/api/pipeline

test-api-scripts:
	$(DOCKER_TEST) tests/api/test_scripts.py

test-flask-app:
	$(DOCKER_TEST) tests/api/test_flask_app.py

run-unit-tests:
	$(DOCKER_TEST_PARALLEL) tests/unit/

get-streamsets-libs: install-streamsets-requirements
	rm -rf streamsets/lib/*
	curl -L https://github.com/anodot/anodot-sdc-stage/releases/download/v1.0.1/anodot-1.0.1.tar.gz -o /tmp/sdc.tar.gz && tar xvfz /tmp/sdc.tar.gz -C streamsets/lib

install-streamsets-requirements:
	pip install --upgrade pip && pip install --target streamsets/python-libs -r streamsets/python_requirements.txt

##-----------------------
## DEV DEPENDENCY TARGETS
##-----------------------
build-dev:
	$(DOCKER_COMPOSE_DEV) up -d --build
	docker exec -i anodot-agent python setup.py develop

run-dev:
	$(DOCKER_COMPOSE_DEV) up -d
	docker exec -i anodot-agent python setup.py develop

bootstrap: clean-docker-volumes run-base-services

clean-docker-volumes:
	rm -rf sdc-data
	rm -rf data
	$(DOCKER_COMPOSE_DEV) down -v

run-base:
	docker-compose up -d agent dc squid dummy_destination

run-base-develop:
	docker-compose up -d agent dc squid dummy_destination
	docker exec -i anodot-agent python setup.py develop

run-base-services:
	$(DOCKER_COMPOSE_DEV) up -d agent dc squid dummy_destination
	docker exec -i anodot-agent python setup.py develop

build-base-services: clean-docker-volumes
	$(DOCKER_COMPOSE_DEV) up -d --build agent dc squid dummy_destination
	docker exec -i anodot-agent python setup.py develop

run-elastic:
	$(DOCKER_COMPOSE_DEV) up -d es

run-influx:
	$(DOCKER_COMPOSE_DEV) up -d influx

run-victoria:
	$(DOCKER_COMPOSE_DEV) up -d victoriametrics

run-kafka: run-zookeeper
	$(DOCKER_COMPOSE_DEV) up -d kafka

run-zookeeper:
	$(DOCKER_COMPOSE_DEV) up -d zookeeper

run-mongo:
	$(DOCKER_COMPOSE_DEV) up -d mongo

run-mysql:
	$(DOCKER_COMPOSE_DEV) up -d mysql

run-postgres:
	$(DOCKER_COMPOSE_DEV) up -d postgres

run-sage:
	docker-compose up -d --build sage

##--------------------------
## COMMON DEPENDENCY TARGETS
##--------------------------
setup-kafka:
	./scripts/upload-test-data-to-kafka.sh

setup-elastic:
	./scripts/upload-test-data-to-elastic.sh

setup-victoria:
	./scripts/upload-test-data-to-victoria.sh

sleep:
	sleep $(SLEEP)

nap:
	sleep $(NAP)
