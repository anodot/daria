global sdc

try:
    sdc.importLock()
    from datetime import datetime
finally:
    sdc.importUnlock()


def validate_event(event, record):
    keys = [key for key in event]
    if len(keys) == 0:
        return False
    for required_key in sdc.userParams.get("REQUIRED_FIELDS", []):
        if required_key not in keys:
            sdc.error.write(record, "Record Error: {} is required".format(sdc.userParams["REQUIRED_FIELDS"]))
            return False
    return True


for rec in sdc.records:
    record = sdc.createRecord('record created ' + str(datetime.now()))
    event = {}
    for k, v in sdc.userParams['EVENT_MAPPING'].items():
        if v not in rec.value:
            continue
        event[k] = rec.value[v]
    if not validate_event(event, record):
        continue
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