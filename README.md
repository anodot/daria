##Python agent
With this CLI tool you can create pipelines in Streamsets Data collector which will 
pull data from different sources and push it to anodot

###Main concepts
- **Source** - This is where you want your data to be pulled from. Available sources: *mongodb*
- **Destination** - Where to put your data. Available destinations: *http client* - Anodot rest api endpoint
- **Pipeline** - pipelines connect sources and destinations with data processing and transformation stages

What pipelines do: 

1. Take data from source
2. If destination is http client - every record is transformed to json object according to 
specs of anodot 2.0 metric protocol 
3. Values are converted to floating point numbers
4. Timestamps are converted to unix timestamp in seconds

Basic flow

1. Create source
2. Create destination
3. Create pipeline
4. Run pipeline
5. Check pipeline status
6. If errors occur - check troubleshooting section
    1. fix errors
    2. Stop the pipeline 
    3. Reset pipeline origin
    4. Run pipeline again

###How to build
```
docker-compose up -d
```

###How to use
Attach to docker container with agent and that's all - you can use CLI
```
docker attach dir_name_agent_1
```
    
###Run tests
Just run `pytest` command inside agent container.   
    
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
    
    
9. List pipelines `pipeline list`
10. Start pipeline `pipeline start PIPELINE_ID`
11. Stop pipeline `pipeline stop PIPELINE_ID`
12. Delete pipeline `pipeline delete PIPELINE_ID`
13. Pipeline info `pipeline info PIPELINE_ID`
    
    Shows current pipeline status, amount of records worked, issues with 
    pipeline configuration if any and history of execution
14. Pipeline logs `pipeline logs --help`
15. Reset pipeline offset `pipeline reset PIPELINE_ID`

###Configuration description

####Sources
- **Mongodb**
    - *Connection string* - database connection string e.g. `mongodb://mongo:27017`
    - *Username*
    - *Password*
    - *Authentication Source* - for delegated authentication, specify alternate database name. 
    Leave blank for normal authentication
    - *Database*
    - *Collection*
    - *Is collection capped*
    - *Initial offset* - Date or id from witch to pull data from
    - *Offset type* - `OBJECTID`, `STRING` or  `DATE`
    - *Offset field*
    - *Batch size* - how many records to send to further pipeline stages
    - *Max batch wait time (seconds)* - how many time to wait until batch will reach it's size

####Destinations
- **Http client** - anodot rest api
    - *Anodot metric api url with token and protocol param* - e.g. `https://api.anodot.com/api/v1/metrics?token=065200eea2dbb29312c41424&protocol=anodot20`
    
####Pipeline
- *Pipeline ID* - unique pipeline identifier (use human-readable name so you could easily use it further) 
- *Measurement name* - what do you measure (this will be the value of `what` property in anodot 2.0 metric protocol)
- *Value type* - column or constant
- *Value* - if type column - enter column name, if type constant - enter value
- *Target type* - represents how samples of the same metric are aggregated in Anodot. Valid values are: 
        `gauge` (average aggregation), `counter` (sum aggregation)
- *Timestamp column name*
- *Timestamp column type*
    - `string` (must specify format)
    - `datetime` (if column has database specific datetime type like `Date` in mongo)
    - `unix_ms` (unix timestamp in milliseconds)
    - `unix` (unix timestamp in seconds)
- *Timestamp format string* - if timestamp column type is string - specify format 
according to this [spec](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html).
- *Required dimensions* - Names of columns delimited with spaces. 
If these fields are missing in a record, it goes to error stage
- *Optional dimensions* - Names of columns delimited with spaces. These fields may be missing in a record
             

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
        
    