### Please note
_- To learn more about Daria agent and its main concepts visit the agent's [Wiki page](https://github.com/anodot/daria/wiki)_

_- It is assumed that the port 80 is forwarded from the agent docker container to the port 8080 on your machine. To
learn more about agent port forwarding visit the [Installation guide](https://github.com/anodot/daria/wiki#how-to-install)_

### Contents
* [Get streamsets](#get-streamsets)
* [Create streamsets](#create-streamsets)
* [Edit streamsets](#edit-streamsets)
* [Delete streamsets](#delete-streamsets)

Get streamsets
---------------
Returns list of configured streamsets

Response codes: `200, 404`

**Request example**:
```
curl -X GET http://localhost:8080/streamsets
```

**Response example**:
```
[
  "http://dc:18630",
  "http://dc2:18630"
]
```

Create streamsets
------------------

Response codes: `200, 400`

Request fields:

| Field                 | Type     | Description         |
|-----------------------|----------|---------------------|
| url                   | required | Streamsets url      |
| agent_external_url    | required | Agent external url  |
| username              | optional | Streamsets username |
| password              | optional | Streamsets password |
                                                   

**Request example**:
```
curl -X POST http://localhost:8080/streamsets \
-H 'Content-Type: application/json' \
-d '[{
    "url": "http://dc:18630",
    "username": "admin",
    "password": "admin",
    "agent_external_url": "http://anodot-agent:8080"
}]'

```

**Response example**:
```
""
```
                                                            | 400           | Provided proxy data is invalid, please double-check proxy uri, username and password        |


Edit streamsets
----------------

Response codes: `200, 400`

Request fields:

| Field                 | Type     | Description         |
|-----------------------|----------|---------------------|
| url                   | required | Streamsets url      |
| agent_external_url    | optional | Agent external url  |
| username              | optional | Streamsets username |
| password              | optional | Streamsets password |

**Request example**:
```
curl -X PUT http://localhost:8080/streamsets \
-H 'Content-Type: application/json' \
-d '[{
    "url": "http://dc:18630",
    "username": "admin",
    "password": "admin,
    "agent_external_url": "http://anodot-agent:8080"
}]'

```

**Response example**:
```
{
""
```


Delete streamsets
------------------

Response codes: `200`

Request example:
```
curl -X DELETE http://localhost:8080/streamsets
```
Response:
```
success
```
