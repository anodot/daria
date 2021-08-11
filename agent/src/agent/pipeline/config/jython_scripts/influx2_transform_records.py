global sdc

try:
    sdc.importLock()
    import sys
    import os
    import collections

    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))

    from datetime import datetime
finally:
    sdc.importUnlock()

DATEFORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


def to_timestamp(date):
    epoch = datetime(1970, 1, 1)
    return (date - epoch).total_seconds()


records = {}
for record in sdc.records:
    # * 1000 because of strange implementaion of 'Add tags and static dimensions', it will divide by 1000 later
    timestamp = to_timestamp(datetime.strptime(record.value[sdc.userParams['TIMESTAMP_COLUMN']], DATEFORMAT)) * 1000
    if timestamp in records:
        r = records[timestamp]
        r[record.value['_field']] = record.value['_value']
        continue
    record.value[record.value['_field']] = record.value['_value']
    record.value[sdc.userParams['TIMESTAMP_COLUMN']] = timestamp
    records[timestamp] = record.value

records = sorted(records.items(), key=lambda x: x[1][sdc.userParams['TIMESTAMP_COLUMN']])
records = collections.OrderedDict(records)

for timestamp, obj in records.items():
    record = sdc.createRecord('record created ' + str(timestamp))
    record.value = obj
    sdc.output.write(record)
