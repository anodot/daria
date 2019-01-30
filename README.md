##Python agent
Wrapper for Streamsets Data Collector

###How to build
```
docker-compose up -d
```

###How to use
1. Attach to docker container with agent and that's all - you can use CLI
    ```
    docker attach dir_name_agent_1
    ```
    
    
###Available commands
1. List available commands 
    ```
    pipeline --help
    ```
2. Create source `pipeline source create`
3. List sources `pipeline source list`
4. Delete source `pipeline source delete`
5. Create destination `pipeline destination create`
6. List destination `pipeline destination list`
7. Delete destination `pipeline destination delete`
8. Create pipelines with config file `pipeline create -f CONFIG_FILE`

    Config schema can be found in `agent/pipeline_config_schema.py`
    
    Config example is in `agent/pipeline_configs/pipeline_config_example.json`
    
    If no file is specified config will be prompted in the console
    
    - `pipeline_id` - unique pipeline identifier
    - `target_type` - if `gauge` aggregation will be performed using average (default), if `counter` - using sum
    - `timestamp` - `name`: column name, `type`: column type, `format`: datetime string format if type is string 
        ([string format spec](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html))
    
        possible types: 
        - `string` (must specify format)
        - `datetime` (if column has database specific datetime type like `Date` in mongo)
        - `unix_ms` (unix timestamp in milliseconds)
        - `unix` (unix timestamp in seconds)
    - `required dimensions` - columns must exist in a record (separate with spaces)
    
    
    
9. List pipelines `pipeline list`
10. Start pipeline `pipeline start PIPELINE_ID`
11. Stop pipeline `pipeline stop PIPELINE_ID`
12. Delete pipeline `pipeline delete PIPELINE_ID`
13. Pipeline info `pipeline info PIPELINE_ID`
    
    Shows current pipeline status, amount of records worked, issues with 
    pipeline configuration if any and history of execution
14. Pipeline logs `pipeline logs --help`
15. Reset pipeline offset `pipeline reset PIPELINE_ID`

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
        
    