global sdc

try:
    sdc.importLock()
    from datetime import datetime
finally:
    sdc.importUnlock()

# todo do I need create categories and probably other things?
REQUIRED = [
    'title',
    'category',
    'source',
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
        val = rec.value[v]
        if k in ['startDate', 'endDate']:
            val = int(val)
        event[k] = val
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
    record.value = {
        'event': event
    }
    sdc.output.write(record)
