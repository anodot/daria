try:
    sdc.importLock()
    import sys
    import os

    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import requests
    import json

    from datetime import datetime, timedelta
finally:
    sdc.importUnlock()

dimensions = ['job', 'instance']
tags = {'level': 'highest'}
target_type = 'counter'
start = 1594113926
step = 100

entityName = ''


def get_metrics():
    return "|".join(['vm_log_messages_total', 'vm_protoparser_read_calls_total'])


cur_batch = sdc.createBatch()
url = 'http://victoriametrics:8428/api/v1/export?match[]={__name__=~"' + get_metrics() + '"}'

while True:
    end = start + step
    response = requests.get(url, stream=True)
    start += end

    metrics = []
    for line in response.iter_lines():
        item = json.loads(line.decode("utf-8"))

        dims = {k: v for k, v in item['metric'].items() if k in dimensions}
        the_thing = {
            'properties': {
                'what': item['metric']['__name__'],
                'target_type': target_type,
            },
            'tags': tags
        }
        for k, v in dims.items():
            the_thing['properties'][k] = v

        for i in range(len(item['values'])):
            tmp = the_thing
            tmp['timestamp'] = item['timestamps'][i] // 1000
            tmp['value'] = item['values'][i]
            record = sdc.createRecord('record created ' + str(datetime.now()))
            record.value = tmp
            cur_batch.add(record)

        cur_batch.process(entityName, str(end))
        cur_batch = sdc.createBatch()
        # if the pipeline has been stopped, we should end the script
        if sdc.isStopped():
            break
