### Please note
_- To learn more about Daria agent and its main concepts visit the agent's [Wiki page](https://github.com/anodot/daria/wiki)_

_- It is assumed that the port 80 is forwarded from the agent docker container to the port 8080 on your machine. To
learn more about agent port forwarding visit the [Installation guide](https://github.com/anodot/daria/wiki#how-to-install)_

### Contents
* [Get pipelines](#get-pipelines)
* [Create pipelines](#create-pipelines)
* [Edit pipelines](#edit-pipelines)
* [Delete pipeline](#delete-pipeline)
* [Start pipeline](#start-pipeline)
* [Stop pipeline](#stop-pipeline)
* [Force stop pipeline](#force-stop-pipeline)
* [Get pipeline info](#get-pipeline-info)
* [Get pipeline logs](#get-pipeline-logs)
* [Enable destination logs](#enable-destination-logs)
* [Disable destination logs](#disable-destination-logs)
* [Reset pipeline](#reset-pipeline)

Get pipelines
-----------
Returns a list of existing pipeline configs

Response codes: `200`

**Request example**:
```
curl -X GET http://localhost:8080/pipelines
```

**Response example**:
```
[
    {
        "override_source": {},
        "pipeline_id": "Monitoring",
        "source": {
            "name": "monitoring"
        }
    }
]
```

Create pipelines
----------------
To create one or multiple pipelines submit a POST request containing pipeline configurations in JSON format to the `/pipelines` endpoint.
All types of pipeline configurations are described in the [Wiki](https://github.com/anodot/daria/wiki)

Response codes: `200, 400`

**Request example**:
```
curl -X POST http://localhost:8080/pipelines \
-H 'Content-Type: application/json' \
-d '[
    {
        "source": "influx",
        "pipeline_id": "test_influx",
        "measurement_name": "cpu_test",
        "value": ["usage_active"],
        "dimensions": {
            "required": [],
            "optional": ["cpu", "host", "zone"]
        },
        "target_type": "gauge",
        "properties": {"test": "val"},
        "interval": 100
    }
]'
```

**Response example**:
```
[
    {
        "dimensions": {
            "optional": [
                "cpu",
                "host",
                "zone"
            ],
            "required": []
        },
        "interval": 100,
        "measurement_name": "cpu_test",
        "override_source": {},
        "pipeline_id": "test_influx",
        "properties": {
            "test": "val"
        },
        "source": {
            "name": "influx"
        },
        "target_type": "gauge",
        "value": {
            "constant": "1",
            "type": "property",
            "values": [
                "usage_active"
            ]
        }
    }
]
```

Edit pipelines
-----------
To edit one or multiple pipelines submit a PUT request containing pipeline configurations in JSON format to the `/pipelines` endpoint.
All types of pipeline configurations are described in the [Wiki](https://github.com/anodot/daria/wiki)

Response codes: `200, 400`

**Request example**:
```
curl -X PUT http://localhost:8080/pipelines \
-H 'Content-Type: application/json' \
-d '[
    {
        "source": "influx",
        "pipeline_id": "test_influx",
        "measurement_name": "different_measurment",
        "value": ["usage_active"],
        "dimensions": {
            "required": [],
            "optional": ["cpu", "host", "zone"]
        },
        "target_type": "gauge",
        "properties": {"test": "val"},
        "interval": 100
    }
]'
```

**Response example**
```
[
    {
        "dimensions": {
            "optional": [
                "cpu",
                "host",
                "zone"
            ],
            "required": []
        },
        "interval": 100,
        "measurement_name": "different_measurment",
        "override_source": {},
        "pipeline_id": "test_influx",
        "properties": {
            "test": "val"
        },
        "source": {
            "name": "influx"
        },
        "target_type": "gauge",
        "value": {
            "constant": "1",
            "type": "property",
            "values": [
                "usage_active"
            ]
        }
    }
]
```

Delete pipeline
-------------
Response codes: `200, 400`

**Request:**
```
curl -X DELETE http://localhost:8080/pipelines/test_influx
```
**Response:**
`Status: 200 OK`

**Request:**
```
curl -X DELETE http://localhost:8080/pipelines/not_existing
```
**Response:**
```
Status: 400 BAD REQUEST

Pipeline not_existing does not exist
```

Start pipeline
-------------
Response codes: `200, 400`

**Request:**
```
curl -X POST http://localhost:8080/pipelines/test_influx/start
```
**Response:**
Status: 200 OK

Stop pipeline
-------------
Response codes: `200, 400`

**Request:**
```
curl -X POST http://localhost:8080/pipelines/test_influx/stop
```
**Response:**
Status: 200 OK

Force stop pipeline
-------------
Response codes: `200, 400`

**Request:**
```
curl -X POST http://localhost:8080/pipelines/test_influx/force-stop
```
**Response:**
Status: 200 OK

Get pipeline info
-----------------
Response codes: `200, 400`

**Request:**
Get arguments:
Argument            | Type    | Description
--------------------|---------|-----------------------------------------------
`number_of_history_records` | Integer | Number of history records to return, default - 10
```
curl -X GET http://localhost:8080/pipelines/test_influx/info
```
**Response:**
```
{
    "history": [
        [
            "2020-07-06 13:25:44",
            "EDITED",
            "Pipeline edited",
            " "
        ]
    ],
    "metric_errors": [],
    "metrics": "",
    "pipeline_issues": [],
    "stage_issues": {},
    "status": "EDITED Pipeline edited"
}
```

Get pipeline logs
-----------------
Response codes: `200, 400`

Get arguments:
Argument            | Type    | Description
--------------------|---------|-----------------------------------------------
`severity`          | String  | Show logs with a specified severity, possible values: `INFO`, `ERROR`, default - `INFO`
`number_of_records` | Integer | Number of log records to return, default - 10

**Request:**
```
curl -X GET http://localhost:8080/pipelines/test_influx/logs?severity=INFO&number_of_records=1
```
**Response:**
```
[
    [
        "2020-07-06 13:14:45,898",
        "INFO",
        "StandaloneAndClusterRunnerProviderImpl",
        "Pipeline execution mode is: STANDALONE "
    ]
]
```

Enable destination logs
-----------------------
Response codes: `200, 400`

**Request:**
```
curl -X POST http://localhost:8080/pipelines/test_influx/enable-destination-logs
```
**Response:**
Status: 200 OK


Disable destination logs
-----------------------
Response codes: `200, 400`

**Request:**
```
curl -X POST http://localhost:8080/pipelines/test_influx/disable-destination-logs
```
**Response:**
Status: 200 OK

Reset pipeline
-----------------------
Response codes: `200, 400`

**Request:**
```
curl -X POST http://localhost:8080/pipelines/test_influx/reset
```
**Response:**
Status: 200 OK
