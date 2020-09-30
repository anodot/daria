global sdc

try:
    sdc.importLock()
    import time
    from datetime import datetime, timedelta
finally:
    sdc.importUnlock()


def get_now_with_delay():
    return int(time.time()) - int(sdc.userParams['INTERVAL_IN_MINUTES']) * 60


def to_timestamp(date):
    epoch = datetime(1970, 1, 1)
    return int((date - epoch).total_seconds())


entityName = ''
interval = timedelta(seconds=int(float(sdc.userParams['INTERVAL_IN_MINUTES']) * 60))

if sdc.lastOffsets.containsKey(entityName):
    offset = int(float(sdc.lastOffsets.get(entityName)))
elif sdc.userParams['INITIAL_OFFSET']:
    offset = to_timestamp(datetime.strptime(sdc.userParams['INITIAL_OFFSET'], '%d/%m/%Y %H:%M'))
else:
    offset = datetime.utcnow().replace(second=0, microsecond=0) - interval

while True:
    if offset > get_now_with_delay():
        time.sleep(offset - get_now_with_delay())
    cur_batch = sdc.createBatch()
    record = sdc.createRecord('record created ' + str(datetime.now()))
    record.value = {'last_timestamp': int(offset) * int(1e9)}
    cur_batch.add(record)
    cur_batch.process(entityName, str(offset))
    offset += interval.total_seconds()