## Python agent
With this CLI tool you can create pipelines in Streamsets Data collector which will 
pull data from different sources and push it to anodot

### How to build
```
docker-compose up -d
```

###How to use
Attach to docker container with agent and that's all - you can use CLI
```
docker attach anodot-agent
```
    
###Run tests
1. Run `./setup_tests.sh`
2. Run `pytest` command inside agent container. 


###Docs
[Github Wiki](https://github.com/anodot/daria/wiki)
    

###Troubleshooting
Pipelines may not work as expected for several reasons, for example wrong configuration, 
or some issues connecting to destination etc. You can look for errors in three locations:

1. `pipeline info PIPELINE_ID`
    This command will show some issues if pipeline is misconfigured
2. `pipeline logs -s ERROR PIPELINE_ID`
    shows error logs if any
3. Also sometimes records may not reach destination because errors
happened in one of data processing and transformation stages. In that case you can find them in error 
files which are placed at `/sdc-data` directory and named with pattern `error-pipelineid-sdcid` 
    (pipeline id without spaces). 
    
    For example to see last ten records for specific pipeline id use this command:
    ```bash
    tail $(ls -t /sdc-data/error-pipelineid* | head -1)
    ```
        
    