global sdc, output

try:
    sdc.importLock()
    import re
    import time
    import sys
    import os
    import json

    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    from anodot_api_client import AnodotApiClient, AnodotUrlBuilder
finally:
    sdc.importUnlock()


# todo ?
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def start_rollup(client):
    res = client.start_topology_data_load()
    if res.status_code != 200:
        sdc.log.error('Error starting rollup')
        sdc.log.error(str(res.json()))
    res.raise_for_status()
    return str(res.json()['rollupId'])


def end_rollup(client, rollup_id):
    res = client.end_topology_data_load(rollup_id)
    if res.status_code != 200:
        sdc.log.error('Error ending rollup')
        sdc.log.error(str(res.json()))
    res.raise_for_status()


def build_entities(base_entity, entities, bulk_ser_number):
    data = base_entity.copy()
    # row must be a json string, because the topology api requires this format
    rows = {entity['id']: json.dumps(entity) for entity in entities}
    data['rows'] = rows
    data['numberOfRows'] = len(rows)
    data['bulkSerNumber'] = bulk_ser_number
    return data


def send_data(client, data, rollup_id):
    res = client.send_topology_data(data, rollup_id)
    if res.status_code != 200:
        sdc.log.error('ERROR SENDING DATA')
        sdc.log.error(str(res.text))
        sdc.log.error('status code ' + str(res.status_code))
    res.raise_for_status()


now = int(time.time())
# todo preview sends data
client = AnodotApiClient(
    sdc.state, sdc.userParams['ANODOT_URL'], sdc.userParams['ACCESS_TOKEN'], sdc.userParams['PROXIES']
)
rollup_id = start_rollup(client)
for record in sdc.records:
    for entity_type, entities in record.value.items():
        base = {
            "type": entity_type,
            "rollupId": rollup_id,
            "timestamp": now,
            "bulkSerNumber": 1,
        }
        for i, chunk in enumerate(chunks(entities, 500)):
            # i starts from 0 and bulkSerNumber starts from 1 so + 1
            data = build_entities(base, chunk, i + 1)
            send_data(client, data, rollup_id)

            new_record = sdc.createRecord(str(i))
            new_record.value = data
            output.write(new_record)

end_rollup(client, rollup_id)
