Get destination
---------------
Request:
```
GET destination/
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
**Response codes:** `200, 404`

Create destination
------------------

Request:
```
POST destination/

Body parameters:
{
    data_collection_token: required
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
