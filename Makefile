SLEEP = 60
DOCKER_COMPOSE_DEV = docker-compose-dev.yml
DOCKER_TEST = docker exec -i anodot-agent pytest

all: build test-all

build:
	docker-compose up -d --build
	sleep $(SLEEP)
	./setup_tests.sh

test-all:
	$(DOCKER_TEST) -x

all-dev: build-dev test-all-dev

build-dev:
	docker-compose -f $(DOCKER_COMPOSE_DEV) up -d --build
	docker exec -i anodot-agent python setup.py install
	sleep $(SLEEP)
	./setup_tests.sh

test-all-dev:
	$(DOCKER_TEST) -x

test-directory: test-destination
	$(DOCKER_TEST) tests/test_directory_http.py

test-elastic: test-destination
	$(DOCKER_TEST) tests/test_elastic_http.py

test-influx: test-destination
	$(DOCKER_TEST) tests/test_influx_http.py

test-kafka: test-destination
	$(DOCKER_TEST) tests/test_kafka_http.py

test-mongo: test-destination
	$(DOCKER_TEST) tests/test_mongo_http.py

test-mysql: test-destination
	$(DOCKER_TEST) tests/test_mysql_http.py

test-postgres: test-destination
	$(DOCKER_TEST) tests/test_postgres_http.py

test-tcp: test-destination
	$(DOCKER_TEST) tests/test_tcp_http.py

test-zpipline: test-destination
	$(DOCKER_TEST) tests/test_zpipline_base.py

test-destination:
	$(DOCKER_TEST) tests/test_destination.py
