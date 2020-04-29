DARIA_AGENT_DOCKER_IMAGE_NAME := anodot/daria
SDC_DOCKER_IMAGE_NAME := anodot/streamsets
APP_VERSION := 1.10.0-beta

all: clean format vet test build build-container test-container

clean:
	docker rmi -f `docker images $(DARIA_AGENT_DOCKER_IMAGE_NAME):$(APP_VERSION) -a -q` || true
	docker rmi -f `docker images $(SDC_DOCKER_IMAGE_NAME):$(APP_VERSION) -a -q` || true

build-container:
	docker build --no-cache -t $(DARIA_AGENT_DOCKER_IMAGE_NAME):$(APP_VERSION) ./agent
	docker build --no-cache -t $(SDC_DOCKER_IMAGE_NAME):$(APP_VERSION) ./streamsets

publish-container: build-container
	docker push $(DARIA_AGENT_DOCKER_IMAGE_NAME):$(APP_VERSION)
	docker push $(SDC_DOCKER_IMAGE_NAME):$(APP_VERSION)