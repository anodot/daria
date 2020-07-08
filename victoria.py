# try:
#     sdc.importLock()
#     import sys
#     import os
#
#     sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
#     import requests
#     import json
#
#     from datetime import datetime, timedelta
# finally:
#     sdc.importUnlock()

import requests
import json

dimensions = ['job', 'instance']
tags = {'level': 'highest'}
target_type = 'counter'
start = 1594113926
step = 100

entityName = ''


def get_metrics():
    return "|".join(['vm_log_messages_total', 'vm_protoparser_read_calls_total'])


# cur_batch = sdc.createBatch()
# url = 'http://localhost:8428/api/v1/export?match[]={__name__=~"' + get_metrics() + '"}'
# url = 'http://localhost:8428/api/v1/export?match[]={__name__!=""}'
url = 'http://localhost:8428/api/v1/export?match={__name__!=""}'
# url = 'http://victoriametrics:8428/api/v1/export?match[]={__name__=~"' + get_metrics() + '"}'

while True:
    end = start + step
    # response = requests.get(url + '&start=' + str(start) + '&end=' + str(end), stream=True)
    response = requests.get(url, stream=True)
    # data = response.content.decode("utf-8")
    start += end

    metrics = []
    # for line in data.splitlines():
    for line in response.iter_lines():
        item = json.loads(line.decode("utf-8"))

        dims = {k: v for k, v in item['metric'].items() if k in dimensions}
        the_thing = {
            'properties': {
                'what': item['metric']['__name__'],
                # **{k: v for k, v in item['metric'].items() if k in dimensions},
                'target_type': target_type,
            },
            'tags': tags
        }
        for k, v in dims.items():
            the_thing['properties'][k] = v

        for i in range(len(item['values'])):
            # metrics.append({**the_thing, **{'timestamp': item['timestamps'][i], 'value': item['values'][i]}})
            tmp = the_thing
            tmp['timestamp'] = item['timestamps'][i]
            tmp['value'] = item['values'][i]
            # cur_batch.add({**the_thing, **{'timestamp': item['timestamps'][i], 'value': item['values'][i]}})
            cur_batch.add(tmp)

        cur_batch.process(entityName, end)
        cur_batch = sdc.createBatch()
        # if the pipeline has been stopped, we should end the script
        if sdc.isStopped():
            break
