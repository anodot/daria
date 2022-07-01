global sdc

try:
    sdc.importLock()
    import json
    import time
    import sys
    import os
    import xml.etree.ElementTree as ET
    from datetime import datetime, timedelta
    from urlparse import urlparse
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


def _process_response_xml(content):
    ret = []
    tree = ET.fromstring(content)

    if not tree:
        return ret

    # tags
    tags_element = tree.find('sensortree/nodes/group/probenode/group')
    tag_group = tags_element.find('name')
    tag_location = tags_element.find('group/name')

    # metrics
    ts_unix = get_now()
    devices = tree.findall('*//device')
    for device in devices:
        device_name = device.find('name')
        sensors = device.findall('sensor')
        for sensor in sensors:
            sensortype = sensor.find('sensortype')
            name = sensor.find('name')
            value = sensor.find('lastvalue_raw')
            prtg_ts = sensor.find('lasttime_raw_utc')
            ret.append({
                sensortype.text: value.text,
                'Host Name': device_name.text,
                'Sensor name': name.text,
                'timestamp_unix': ts_unix,
                '__tags': {
                    'Group': [tag_group.text],
                    'Location': [tag_location.text],
                },
            })
    return ret


def _process_response_json(content):
    ret = []
    json_data = json.loads(content)

    if 'sensors' not in json_data:
        return ret
    ts_unix = get_now()
    for item in json_data['sensors']:
        ret.append({
            item['sensor_raw']: item.get('lastvalue_raw') or None,
            'Host Name': item.get('device_raw'),
            'Sensor name': item.get('sensor'),
            'timestamp_unix': ts_unix,
            '__tags': {
                'Group': [item.get('group_raw')],
            },
        })
    return ret


entityName = ''


def main():
    interval = timedelta(seconds=get_interval())
    if sdc.lastOffsets.containsKey(entityName):
        offset = int(float(sdc.lastOffsets.get(entityName)))
    else:
        offset = to_timestamp(datetime.utcnow().replace(second=0, microsecond=0))

    sdc.log.info('OFFSET: ' + str(offset))

    while True:
        if sdc.isStopped():
            break
        while offset > get_now():
            time.sleep(1)
            if sdc.isStopped():
                return

        data = []
        session = requests.Session()
        cur_batch = sdc.createBatch()
        if sdc.userParams['USERNAME']:
            session.auth = (sdc.userParams['USERNAME'], sdc.userParams['PASSWORD'])
        if offset - get_interval() < get_now():
            offset = get_now() + get_interval()

        try:
            res = session.get(sdc.userParams['URL'], verify=sdc.userParams['VERIFY_SSL'])
            res.raise_for_status()
            url_parsed = urlparse(sdc.userParams['URL'])
            if url_parsed.path.endswith('.xml'):
                data = _process_response_xml(res.content)
            elif url_parsed.path.endswith('.json'):
                data = _process_response_json(res.content)

            for value_dict in data:
                record = sdc.createRecord('record created ' + str(datetime.now()))
                record.value = value_dict
                record.value['last_timestamp'] = int(offset)
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
        except requests.HTTPError as e:
            requests.post(sdc.userParams['MONITORING_URL'] + str(e.response.status_code))
            sdc.log.error(str(e))


main()
