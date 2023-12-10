### Please note
_- To learn more about Daria agent and its main concepts visit the agent's [Wiki page](https://github.com/anodot/daria/wiki)_

_- It is assumed that the port 80 is forwarded from the agent docker container to the port 8080 on your machine. To
learn more about agent port forwarding visit the [Installation guide](https://github.com/anodot/daria/wiki#how-to-install)_

### Contents
* [Get destination](#get-destination)
* [Create destination](#create-destination)
* [Edit destination](#edit-destination)
* [Delete destination](#delete-destination)

Get destination
---------------
Returns destination configuration if it exists

Response codes: `200, 404`

**Request example**:
```
curl -X GET http://localhost:8080/destination
```

**Response example**:
```
{
    "access_key": "correct_key",
    "config": {
        "conf.client.useProxy": true,
        "conf.client.proxy.uri": "http://squid:3128",
        "conf.client.proxy.username": "",
        "conf.client.proxy.password": "",
        "token": "correct_token",
        "url": "http://dummy_destination"
    },
    "host_id": "ABCDEF",
    "type": "http"
}
```

Create destination
------------------

Response codes: `200, 400`

Request fields:
| Field                 | Type     | Description                                                                                                                                          |
|-----------------------|----------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| data_collection_token | required | Anodot data collection token                                                                                                                         |
| destination_url       | required | An url of an Anodot application where all data will be transferred. Example: 'https://api.anodot.com' |
| access_key            | optional | Anodot access key                                                                                                                                    |
| proxy_uri             | optional | URI of a proxy that will be used to connect to the destination                                                                                       |
| proxy_username        | optional | Username for proxy authentication                                                                                                                    |
| proxy_password        | optional | Password for proxy authentication                                                                                                                    |
| host_id               | optional | A unique identifier of your host machine. If not provided, a random string will be used                                                              |

**Request example**:
```
curl -X POST http://localhost:8080/destination \
-H 'Content-Type: application/json' \
-d '{
    "data_collection_token":"data_collection_token",
    "destination_url":"https://api.anodot.com",
    "access_key": "access_key",
    "proxy_uri": "https://example-proxy.com",
    "proxy_username": "user",
    "proxy_password": "pass",
    "host_id": "my_host"
}'

```

**Response example**:
```
{
    "access_key": "access_key",
    "config": {
        "conf.client.useProxy": true,
        "conf.client.proxy.uri": "https://example-proxy.com",
        "conf.client.proxy.password": "pass",
        "conf.client.proxy.username": "user",
        "token": "data_collection_token",
        "url": "https://api.anodot.com"
    },
    "host_id": "my_host",
    "type": "http"
}
```

Response errors:
| Error                                                                                | Response code | Description                                                                                 |
|--------------------------------------------------------------------------------------|---------------|---------------------------------------------------------------------------------------------|
| "destination_url": ["Wrong url format, please specify the protocol and domain name"] | 400           | URL you provided has incorrect format, make sure you specified the protocol (http, https)   |
| Data collection token is invalid                                                     | 400           | To get a valid token see [Basic flow](https://github.com/anodot/daria/wiki#basic-flow)      |
| Destination URL is invalid                                                           | 400           | Make sure you provided a valid Anodot application url                                       |
| Access key is invalid                                                                | 400           | To get a valid access key see [Instructions](https://support.anodot.com/hc/en-us/articles/360002631114-Token-Management-#AccessKeys) |
| Proxy data is invalid                                                                | 400           | Provided proxy data is invalid, please double-check proxy uri, username and password        |


Edit destination
----------------
You can pass any parameters to rewrite them in the existing destination.

Response codes: `200, 400`

Request fields:
| Field                 | Type     | Description                                                       |
|-----------------------|----------|-------------------------------------------------------------------|
| data_collection_token | optional | Anodot data collection token                                      |
| destination_url       | optional | A url of an Anodot application where all data will be transferred |
| access_key            | optional | Anodot access key                                                 |
| proxy_uri             | optional | URI of a proxy that will be used to connect to the destination    |
| proxy_username        | optional | Username for proxy authentication                                 |
| proxy_password        | optional | Password for proxy authentication                                 |
| host_id               | optional | A unique identifier of your host machine                          |

**Request example**:
```
curl -X PUT http://localhost:8080/destination \
-H 'Content-Type: application/json' \
-d '{
    "data_collection_token":"new_collection_token",
    "destination_url":"https://new.anodot.com",
    "access_key": "new_access_key",
    "proxy_uri": "https://new-example-proxy.com",
    "proxy_username": "user",
    "proxy_password": "pass",
    "host_id": "new_host"
}'

```

**Response example**:
```
{
    "access_key": "new_access_key",
    "config": {
        "conf.client.useProxy": true,
        "conf.client.proxy.uri": "https://new-example-proxy.com",
        "conf.client.proxy.username": "user",
        "conf.client.proxy.password": "pass",
        "token": "new_token",
        "url": "https://new.anodot.com"
    },
    "host_id": "new_host",
    "type": "http"
}
```

Response errors:
| Error                                                                                | Response code | Description                                                                                 |
|--------------------------------------------------------------------------------------|---------------|---------------------------------------------------------------------------------------------|
| "destination_url": ["Wrong url format, please specify the protocol and domain name"] | 400           | URL you provided has incorrect format, make sure you specified the protocol (http, https)   |
| Data collection token is invalid                                                     | 400           | To get a valid token see [Basic flow](https://github.com/anodot/daria/wiki#basic-flow)      |
| Destination URL is invalid                                                           | 400           | Make sure you provided a valid Anodot application url                                       |
| Access key is invalid                                                                | 400           | To get a valid access key see [Instructions](https://support.anodot.com/hc/en-us/articles/360002631114-Token-Management-#AccessKeys) |
| Proxy data is invalid                                                                | 400           | Provided proxy data is invalid, please double-check proxy uri, username and password        |


Delete destination
------------------

Response codes: `200`

Request example:
```
curl -X DELETE http://localhost:8080/destination
```
Response:
```
success
```
