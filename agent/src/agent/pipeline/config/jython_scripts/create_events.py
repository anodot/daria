global sdc

try:
    sdc.importLock()
    from datetime import datetime
finally:
    sdc.importUnlock()

REQUIRED = [
    'title',
    'category',
    # it will be required if it's not hardcoded
    # 'source',
    'startDate'
]


for rec in sdc.records:
    record = sdc.createRecord('record created ' + str(datetime.now()))
    event = {}
    for k, v in sdc.userParams['EVENT_MAPPING'].items():
        if k == 'properties':
            continue
        if v not in rec.value:
            if v in REQUIRED:
                raise Exception('Missing required field: ' + v)
            continue
        event[k] = rec.value[v]
    event['properties'] = []
    for prop in sdc.userParams['EVENT_MAPPING']['properties']:
        prop = {
            'key': prop,
            'value': rec.value[prop],
        }
        event['properties'].append(prop)
    event['properties'].append({
        'key': 'pipeline_id',
        'value': '${pipeline:id()}'
    })
    # this is hardcoded for all events for now
    event['source'] = 'Agent'
    record.value = {
        'event': event
    }
    sdc.output.write(record)
