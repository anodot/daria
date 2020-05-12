[![Latest Release](https://img.shields.io/github/release/anodot/daria.svg)](https://github.com/anodot/daria/releases/latest)
[![Docker pulls](https://img.shields.io/docker/pulls/anodot/daria.svg)](https://hub.docker.com/r/anodot/daria)

# Anodot Daria agent
With this CLI tool you can create pipelines in Streamsets Data collector which will 
pull data from different sources and push it to anodot

## How to use
To use the CLI you need to build and run docker containers and then attach to the agent container.
Currently there are two versions of the agent: release and dev.

You need to rebuild the release version of the agent every time you change code in it. Dev version will pull changes on the fly.
To build the agent run
```
make build-all
```
to build a release version or
```
make build-all-dev
```
to build a dev version.

To attach to the agent container run
```
docker attach anodot-agent
```
    
## Run tests
To run all tests on a dev or release version simply run
```
make all
```
or
```
make all-dev
```
correspondingly. It will build all containers and run all tests.

You can also test only a specific source, to do that you can run ```make test-resource-name```, for example
```
make test-kafka
```

## Docs
[Github Wiki](https://github.com/anodot/daria/wiki)
