# Send data from kafka topic to anodot
#### Send topology data from kafka topic to `/api/v2/topology/data` endpoint

#### Important
Before using the script add [access key](https://support.anodot.com/hc/en-us/articles/360002631114-Token-Management-)
to the [agent destination](https://github.com/anodot/daria/wiki/CLI-reference#destination)
```
agent destination
```

#### Usage example:
```
docker exec -it anodot-agent python /usr/src/app/scripts/kafka_topology/run.py --brokers kafka:29092 --topic test_csv --type ring
```
Type can be one of `ring`, `zipcode`, `ncr`
