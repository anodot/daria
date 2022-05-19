global sdc, output, error

try:
    sdc.importLock()
    import sys
    import os

    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import requests
    import re
    import time
finally:
    sdc.importUnlock()

entityName = ''


def get_interval():
    return int(sdc.userParams['INTERVAL_IN_SECONDS'])


def get_now_with_delay():
    return int(time.time()) - int(sdc.userParams['DELAY_IN_MINUTES']) * 60


def main():
    if sdc.lastOffsets.containsKey(entityName):
        offset = int(float(sdc.lastOffsets.get(entityName)))
    else:
        offset = int(time.time())

    while not sdc.isStopped():
        now = get_now_with_delay()
        while offset > now:
            # todo I guess it might shift data sending all the time because sleep might oversleep a bit
            # todo and then we add interval, not interval - overslept time
            time.sleep(1)
            if sdc.isStopped():
                return
        offset = now + get_interval()

        batch = sdc.createBatch()
        res = requests.get(sdc.userParams['TOPOLOGY_SOURCE_URL'])
        res.raise_for_status()

        record = sdc.createRecord('record created')
        record.value = res.json()
        batch.add(record)

        batch.process(entityName, str(offset))


main()
