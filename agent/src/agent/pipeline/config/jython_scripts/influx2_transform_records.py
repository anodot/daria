global sdc

try:
    sdc.importLock()
    import sys
    import os

    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))

    from datetime import datetime
finally:
    sdc.importUnlock()

DATEFORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


def to_timestamp(date):
    epoch = datetime(1970, 1, 1)
    return (date - epoch).total_seconds()


records = []
for record in sdc.records:
    timestamp = to_timestamp(datetime.strptime(record.value[sdc.userParams['TIMESTAMP_COLUMN']], DATEFORMAT))
    if '_field' in record.value.keys():
        record.value[record.value['_field']] = record.value['_value']
    else:
        for name in sdc.userParams['VARIABLES']:
            field_name = '_field_' + name
            value_name = '_value_' + name
            if not sdc.getFieldNull(record, '/' + field_name) or not sdc.getFieldNull(record, '/' + value_name):
                continue
            record.value[record.value[field_name]] = record.value[value_name]
    record.value[sdc.userParams['TIMESTAMP_COLUMN']] = timestamp
    records.append(record.value)

records = sorted(records, key=lambda x: x[sdc.userParams['TIMESTAMP_COLUMN']])

for obj in records:
    record = sdc.createRecord('record created ' + str(obj[sdc.userParams['TIMESTAMP_COLUMN']]))
    record.value = obj
    sdc.output.write(record)
