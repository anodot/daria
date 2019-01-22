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
                "target_type": {"type": "string", "enum": ["counter", "gauge"]},
                "timestamp": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "type": {"type": "string", "enum": ["string", "datetime", "unix", "unix_ms"]},
                        "format": {"type": "string"}
                    },
                    "required": ["name", "type"]
                },
                "dimensions": {
                    "type": "object",
                    "properties": {
                        "required": {"type": "array", "items": {"type": "string"}},
                        "optional": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["required"]},
                "destination_url": {"type": "string"}
            },
            "required": ["pipeline_id", "source_name", "source_config", "measurement_name", "value_field_name",
                         "dimensions", "timestamp", "destination_url"]}
    }
    ```
    - `pipeline_id` - unique pipeline identifier
    - `target_type` - if `gauge` aggregation will be performed using average (default), if `counter` - using sum
    - `timestamp` - `name`: column name, `type`: column type, `format`: datetime string format if type is string 
        ([string format spec](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html))
    
        possible types: 
        - `string` (must specify format)
        - `datetime` (if column has database specific datetime type like `Date` in mongo)
        - `unix_ms` (unix timestamp in milliseconds)
        - `unix` (unix timestamp in seconds)
    - `dimensions` - `required` columns must exist in a record
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
9. Reset pipeline offset `pipeline reset PIPELINE_ID`

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
        
    