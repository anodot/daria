global sdc

try:
    sdc.importLock()
    import time
    from datetime import datetime, timedelta
    import sys
    import os
    import xml.etree.ElementTree as ET
    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import requests
    import pytz
finally:
    sdc.importUnlock()


def get_interval():
    return int(sdc.userParams['INTERVAL_IN_SECONDS'])


def get_now():
    return int(time.time())


def to_timestamp(date):
    epoch = datetime(1970, 1, 1)
    return int((date - epoch).total_seconds())


def prtg_ts_to_unix_ts(prtg_ts, tz=pytz.timezone(sdc.userParams['TIMEZONE'])):
    return datetime.fromtimestamp((prtg_ts - 25569) * 86400)


def _filter(list_):
    return list(filter(lambda x: bool(x), list_))


entityName = ''


def main():
    interval = timedelta(seconds=get_interval())
    if sdc.lastOffsets.containsKey(entityName):
        offset = int(float(sdc.lastOffsets.get(entityName)))
    else:
        offset = to_timestamp(datetime.utcnow().replace(minute=0, second=0, microsecond=0))

    sdc.log.info('OFFSET: ' + str(offset))

    while True:
        if sdc.isStopped():
            break
        while offset > get_now():
            time.sleep(1)
            if sdc.isStopped():
                return

        tree = None
        session = requests.Session()
        if sdc.userParams['USERNAME']:
            session.auth = (sdc.userParams['USERNAME'], sdc.userParams['PASSWORD'])
        if offset - get_interval() < get_now():
            offset = get_now() + get_interval()
        try:
            res = session.get(sdc.userParams['URL'], verify=sdc.userParams['VERIFY_SSL'])
            res.raise_for_status()
            tree = ET.fromstring(res.content)
        except requests.HTTPError as e:
            requests.post(sdc.userParams['MONITORING_URL'] + str(e.response.status_code))
            sdc.log.error(str(e))

        cur_batch = sdc.createBatch()
        record = sdc.createRecord('record created ' + str(datetime.now()))
        if tree:
            # tags
            tags_element = tree.find('sensortree/nodes/group/probenode/group')
            tag_group = tags_element.find('name')
            tag_location = tags_element.find('group/name')

            # metrics
            devices = tree.findall('*//device')
            for device in devices:
                device_name = device.find('name')
                sensors = device.findall('sensor')
                for sensor in sensors:
                    sensortype = sensor.find('sensortype')
                    name = sensor.find('name')
                    value = sensor.find('lastvalue_raw')
                    prtg_ts = sensor.find('lasttime_raw_utc')
                    record.value = {
                        sensortype.text: value.text,
                        'Host Name': device_name.text,
                        'Sensor name': name.text,
                        'timestamp_unix': to_timestamp(prtg_ts_to_unix_ts(float(prtg_ts.text))),
                        'last_timestamp': int(offset),
                        '__tags': {
                            'Group': [tag_group.text],
                            'Location': [tag_location.text],
                        },
                    }
                    cur_batch.add(record)
                    if cur_batch.size() == sdc.batchSize:
                        cur_batch.process(entityName, str(offset))
                        cur_batch = sdc.createBatch()
                        if sdc.isStopped():
                            break
        else:
            record = sdc.createRecord('record created ' + str(datetime.now()))
            record.value = {'last_timestamp': int(offset)}
            cur_batch.add(record)

        cur_batch.process(entityName, str(offset))
        offset += interval.total_seconds()


main()