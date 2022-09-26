global sdc

try:
    sdc.importLock()
    from datetime import datetime
finally:
    sdc.importUnlock()

for rec in sdc.records:
    record = sdc.createRecord('record created ' + str(datetime.now()))
    event = {}
    for k, v in sdc.userParams['EVENT_MAPPING'].items():
        if v not in rec.value:
            continue
        event[k] = rec.value[v]
    event['properties'] = []
    for prop in sdc.userParams['properties']:
        prop = {
            'key': prop,
            'value': rec.value[prop],
        }
        event['properties'].append(prop)
    event['properties'].append({'key': 'pipeline_id', 'value': '${pipeline:id()}'})
    # these are hardcoded for all events for now
    event['source'] = 'Agent'
    event['type'] = 'SUPPRESS'
    if rec.value.get('last_timestamp'):
      offset = rec.value['last_timestamp']
    else:
      offset = rec.attributes['offset']
    record.value = {'event': event, 'offset': offset}
    sdc.output.write(record)
