### Please note
_- To learn more about Daria agent and its main concepts visit the agent's [Wiki page](https://github.com/anodot/daria/wiki)_

_- It is assumed that the port 80 is forwarded from the agent docker container to the port 8080 on your machine. To
learn more about agent port forwarding visit the [Installation guide](https://github.com/anodot/daria/wiki#how-to-install)_

### Contents
* [Get sources](#get-sources)
* [Create source](#create-source)
* [Edit source](#edit-source)
* [Delete source](#delete-source)

Get sources
-----------
Returns a list of existing sources

Response codes: `200`

**Request example**:
```
curl -X GET http://localhost:8080/sources
```

**Response example**:
```
["mongo_source", "elastic_source"]
```

Create source
-------------
To create one or multiple sources submit a POST request containing their configuration in JSON format to the `/sources` endpoint.
All types of source configurations are described in the [Wiki](https://github.com/anodot/daria/wiki)

Response codes: `200, 400`

**Request example**:
```
curl -X POST http://localhost:8080/sources \
-H 'Content-Type: application/json' \
-d '[
    {
        "type": "influx",
        "name": "influx_source",
        "config": {
            "host": "http://influx:8086",
            "db": "test"
        }
    },
    {
        "type": "kafka",
        "name": "kafka_source",
        "config": {
            "version": "2.0+",
            "conf.brokerURI": "kafka:29092",
            "conf.kafkaOptions": ["key:value"],
            "conf.topicList": ["test"],
            "conf.numberOfThreads": 1,
            "conf.kafkaAutoOffsetReset": "EARLIEST",
            "conf.dataFormat": "JSON",
            "conf.maxBatchSize": 1000,
            "conf.batchWaitTime": 10
        }
    }
]'
```

**Response example**:
```
[
    {
        "config": {
            "db": "test",
            "host": "http://influx:8086"
        },
        "name": "influx_source",
        "type": "influx"
    },
    {
        "config": {
            "conf.batchWaitTime": 10,
            "conf.brokerURI": "kafka:29092",
            "conf.dataFormat": "JSON",
            "conf.kafkaAutoOffsetReset": "EARLIEST",
            "conf.kafkaOptions": [
                "key:value"
            ],
            "conf.maxBatchSize": 1000,
            "conf.numberOfThreads": 1,
            "conf.topicList": [
                "test"
            ],
            "library": "streamsets-datacollector-apache-kafka_2_0-lib",
            "version": "2.0+"
        },
        "name": "kafka_source",
        "type": "kafka"
    }
]
```

Edit source
-----------
To edit one or multiple sources submit a PUT request containing their configuration in JSON format to the `/sources` endpoint.
All types of source configurations are described in the [Wiki](https://github.com/anodot/daria/wiki)

Response codes: `200, 400`

**Request example**:
```
curl -X PUT http://localhost:8080/sources \
-H 'Content-Type: application/json' \
-d '[{
    "name": "kafka_source",
    "config": {
        "version": "2.0+",
        "conf.brokerURI": "http://kafka:29092",
        "conf.kafkaOptions": ["key1:value1"],
        "conf.topicList": ["test1"],
        "conf.numberOfThreads": 2,
        "conf.kafkaAutoOffsetReset": "EARLIEST",
        "conf.dataFormat": "JSON",
        "conf.maxBatchSize": 500,
        "conf.batchWaitTime": 5
    }
}]'
```

**Response example**
```
[
    {
        "config": {
            "conf.batchWaitTime": 5,
            "conf.brokerURI": "http://kafka:29092",
            "conf.dataFormat": "JSON",
            "conf.kafkaAutoOffsetReset": "EARLIEST",
            "conf.kafkaOptions": [
                "key1:value1"
            ],
            "conf.maxBatchSize": 500,
            "conf.numberOfThreads": 2,
            "conf.topicList": [
                "test1"
            ],
            "library": "streamsets-datacollector-apache-kafka_2_0-lib",
            "version": "2.0+"
        },
        "name": "kafka_source",
        "type": "kafka"
    }
]
```

Delete source
-------------
To delete a source submit a DELETE request to the `sources/<source_id>` endpoint

Response codes: `200, 400`

**Request:**
```
curl -X DELETE http://localhost:8080/sources/influx_source
```
**Response:**
Status: 200 OK

**Request:**
```
curl -X DELETE http://localhost:8080/sources/not_existing
```
**Response:**
Status: 400 BAD REQUEST

Source config not_existing doesn't exist
