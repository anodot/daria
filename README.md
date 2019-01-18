##Python agent
Wrapper for Streamsets Data Collector

###How to build
```
docker-compose up -d
```

###How to use
1. Attach to docker container with agent
    ```
    docker attach dir_name_agent_1
    ```
2. List available commands 
    ```
    pipeline --help
    ```
3. Create pipelines with `pipeline create [CONFIG_FILE]`
    
    config file format - `json`
    
    [schema](https://json-schema.org/latest/json-schema-validation.html#rfc.section.6.5.3):
    ```json
    {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "pipeline_id": {"type": "string"}, 
                "source_name": {"type": "string", "enum": ["mongo"]},
                "source_config": {"type": "object", "properties": {
                    "configBean.mongoConfig.connectionString": {"type": "string"},
                    "configBean.mongoConfig.username": {"type": "string"},
                    "configBean.mongoConfig.password": {"type": "string"},
                    "configBean.mongoConfig.database": {"type": "string"},
                    "configBean.mongoConfig.collection": {"type": "string"},
                    "configBean.mongoConfig.isCapped": {"type": "boolean"},
                    "configBean.mongoConfig.initialOffset": {"type": "string"}
                }},
                "measurement_name": {"type": "string"},
                "value_field_name": {"type": "string"},
                "timestamp_field_name": {"type": "string"},
                "dimensions": {"type": "array", "items": {"type": "string"}},
                "destination_url": {"type": "string"}
            },
            "required": ["name", "source_name", "source_config", "measurement_name", "value_field_name", "dimensions",
                         "timestamp_field_name", "destination_url"]}
    }
    ```
    - `name` - unique pipeline identifier
    - `timestamp_field_name` - timestamp field must be usix timestamp
    - `destination_url` - anodot metric api url with token and protocol params
    
    Config example is in `agent/pipeline_configs/pipeline_config_example.json`
    
3. List pipelines `pipeline list`
4. Start pipeline `pipeline start PIPELINE_ID`
5. Stop pipeline `pipeline stop PIPELINE_ID`
6. Delete pipeline `pipeline delete PIPELINE_ID`
7. Pipeline info `pipeline info PIPELINE_ID`
    
    Shows current pipeline status, amount of records worked, issues with 
    pipeline configuration if any and history of execution
8. Pipeline logs `pipeline logs --help`

###Troubleshooting
Pipelines may not work as expected for several reasons, for example wrong configuration, 
or some issues connecting to destination etc. You can look for errors in three locations:
1. `pipeline info PIPELINE_ID`
    This command will show some issues if pipeline is misconfigured
2. `pipeline logs -s ERROR PIPELINE_ID`
    shows error logs if any
3. Also sometimes records may not reach destination because errors
happened in one of data processing and transformation stages. In that case you can find them in error 
files in streamsets conatainer
    1. Connect to streamsets container
        ```
        docker exec -it dir_name_dc_1 bash
        ```
    2. Error files are placed at /data directory and named with pattern `error-pipelineid-sdcid` 
    (pipeline id without spaces). For example to see last ten records for specific pipeline id use this command:
        ```bash
        tail $(ls -t /data/error-pipelineid* | head -1)
        ```
        
    