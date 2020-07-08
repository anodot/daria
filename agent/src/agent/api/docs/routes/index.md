### Please note
It is assumed that the port 80 is forwarded from the agent docker container to the port 8080 on your machine. To
learn more about agent port forwarding visit the [Installation guide](https://github.com/anodot/daria/wiki#how-to-install)

Daria Agent REST API
=============

[Destination](destination.md)

[Sources](sources.md)

[Pipelines](pipelines.md)

Get Agent Version
-----------------
**Request**:
```
curl -X GET http://localhost:8080/version
```

**Response example**:
```
"Daria Agent version: 1.16.2"
```
