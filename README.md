## Python agent
With this CLI tool you can create pipelines in Streamsets Data collector which will 
pull data from different sources and push it to anodot

### How to build
```
docker-compose up -d
```

### How to use
Attach to docker container with agent and that's all - you can use CLI
```
docker attach anodot-agent
```
    
### Run tests
1. Run `./setup_tests.sh`
2. Run `pytest` command inside agent container. 


### Docs
[Github Wiki](https://github.com/anodot/daria/wiki)
    

### Dev env
```
docker-compose -f docker-compose-dev.yml up -d --build
docker attach anodot-agent
python setup.py develop
```
Now when you change the code you don't need to rebuild the image
