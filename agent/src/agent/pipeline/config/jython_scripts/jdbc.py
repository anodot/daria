global sdc

try:
    sdc.importLock()
    import time
    from datetime import datetime, timedelta
finally:
    sdc.importUnlock()


def get_interval():
    return int(sdc.userParams['INTERVAL_IN_SECONDS'])


def get_now_with_delay():
    return int(time.time()) - int(sdc.userParams['DELAY_IN_SECONDS'])


def to_timestamp(date):
    epoch = datetime(1970, 1, 1)
    return int((date - epoch).total_seconds())


entityName = ''
interval = timedelta(seconds=get_interval())

if sdc.lastOffsets.containsKey(entityName):
    offset = int(float(sdc.lastOffsets.get(entityName)))
elif sdc.userParams['INITIAL_OFFSET']:
    offset = to_timestamp(datetime.strptime(sdc.userParams['INITIAL_OFFSET'], '%d/%m/%Y %H:%M'))
else:
    offset = to_timestamp(datetime.utcnow().replace(second=0, microsecond=0) - interval)

sdc.log.info('OFFSET: ' + str(offset))

while True:
    if sdc.isStopped():
        break
    now_with_delay = get_now_with_delay() - interval.total_seconds()
    if offset > now_with_delay:
        time.sleep(offset - now_with_delay)
    cur_batch = sdc.createBatch()
    record = sdc.createRecord('record created ' + str(datetime.now()))
    record.value = {'last_timestamp': int(offset)}
    offset += interval.total_seconds()
    cur_batch.add(record)
    cur_batch.process(entityName, str(offset))
