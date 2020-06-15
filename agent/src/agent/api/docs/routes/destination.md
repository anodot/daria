### Please note
_- To learn more about the Daria agent and its main concepts visit the agent's [Wiki page](https://github.com/anodot/daria/wiki)_

_- It is assumed that the port 80 is forwarded from the agent docker container to the port 8080 on your machine. To
learn more about agent port forwarding visit [Installation guide](https://github.com/anodot/daria/wiki#how-to-install)_
###Contents
* [Get destination](#get-destination])
* [Create destination](#create-destination)
* [Edit destination](#edit-destination)
* [Delete destination](#delete-destination)

Get destination
---------------
Returns destination configuration if it exists


Request example:
```
curl -X GET http://localhost:8080/destination/
```

**Possible response codes:** `200, 404`

Response example:
```
{
    "config": {
        "conf.client.useProxy": true,
        "conf.client.proxy.uri": "http://squid:3128",
        "conf.client.proxy.username": "",
        "conf.client.proxy.password": "",
        "conf.resourceUrl": "http://dummy_destination/api/v1/metrics?token=correct_token&protocol=anodot20",
        "monitoring_url": "http://dummy_destination/api/v1/agents?token=correct_token",
        "token": "correct_token",
        "url": "http://dummy_destination"
    },
    "access_key": "correct_key",
    "host_id": "ABCDEF",
    "type": "http"
}
```

Create destination
------------------
Create a new destination with specified parameters.

Request fields:
| Field                 | Type     | Description                                                                                                                               |
|-----------------------|----------|-------------------------------------------------------------------------------------------------------------------------------------------|
| data_collection_token | required | Anodot data collection token                                                                                                              |
| destination_url       | optional |  If the value is not provided, default value 'https://app.anodot.com' will be used |
| access_key            | optional | Anodot access key                                                                                                                         |
| proxy_uri             | optional | URI of a proxy that will be used to connect to the destination                                                                            |
| proxy_password        | optional | Password for proxy authentication                                                                                                         |
| proxy_username        | optional | Username for proxy authentication                                                                                                         |
| host_id               | optional | A unique identifier of your host machine. If not provided, a random string will be used                                                   |

Request example:
```
curl -X POST http://localhost:8080/destination/ \
-H 'Content-Type: application/json' \
-d '{
    "data_collection_token":"data_collection_token",
    "destination_url":"https://app.anodot.com",
    "access_key": "access_key",
    "proxy_uri": "https://example-proxy.com"
    "proxy_username": "user"
    "proxy_password": "pass"
    "host_id": "my_host",
}

```
**Possible response codes:** `200, 400`

Response errors:
| Error                                                                                | Response code | Description                                                                                 |
|--------------------------------------------------------------------------------------|---------------|---------------------------------------------------------------------------------------------|
| "destination_url": ["Wrong url format, please specify the protocol and domain name"] | 400           | URL you provided has incorrect format, make sure you specified the protocol (http, https)   |
| Data collection token is invalid                                                     | 400           | To get a valid token see [Basic flow](https://github.com/anodot/daria/wiki#basic-flow)      |
| Destination URL is invalid                                                           | 400           | Make sure you provided a valid Anodot application url                                       |
| Access key is invalid                                                                | 400           | To get a valid access key see [Basic flow](https://github.com/anodot/daria/wiki#basic-flow) |

Response example:
```
{
    "access_key": "correct_key",
    "config": {
        "conf.client.useProxy": true,
        "conf.client.proxy.uri": "http://squid:3128",
        "conf.client.proxy.password": "",
        "conf.client.proxy.username": "",
        "url": "http://dummy_destination"
        "token": "correct_token",
        "conf.resourceUrl": "http://dummy_destination/api/v1/metrics?token=correct_token&protocol=anodot20",
        "monitoring_url": "http://dummy_destination/api/v1/agents?token=correct_token",
    },
    "host_id": "ABCDEF",
    "type": "http"
}
```

Edit destination
----------------

Request:
```
PUT destination/

Body parameters:
{
    data_collection_token: optional
    destination_url: optional
    access_key: optional
    host_id: optional
    proxy_uri: optional
    proxy_username: optional
    proxy_password: optional
}

```
Response example:
```
{
    "access_key": "correct_key",
    "config": {
        "conf.client.proxy.password": "",
        "conf.client.proxy.uri": "http://squid:3128",
        "conf.client.proxy.username": "",
        "conf.client.useProxy": true,
        "conf.resourceUrl": "http://dummy_destination/api/v1/metrics?token=correct_token&protocol=anodot20",
        "monitoring_url": "http://dummy_destination/api/v1/agents?token=correct_token",
        "token": "correct_token",
        "url": "http://dummy_destination"
    },
    "host_id": "ABCDEF",
    "type": "http"
}
```
**Response codes:** `200, 400`

Delete destination
------------------
Request:
```
DELETE destination/
```
Response:
```
success
```
**Response codes:** `200`
