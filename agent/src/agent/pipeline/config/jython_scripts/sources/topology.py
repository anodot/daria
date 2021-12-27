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

    while True:
        if sdc.isStopped():
            break
        while offset > get_now_with_delay():
            time.sleep(2)
            if sdc.isStopped():
                return
        batch = sdc.createBatch()
        res = requests.get(sdc.userParams['TOPOLOGY_SOURCE_URL'])
        res.raise_for_status()

        for i, row in enumerate(res):
            record = sdc.createRecord('record created ' + str(i))
            record.value = row
            batch.add(record)

        batch.process(entityName, str(time.time()))


main()
