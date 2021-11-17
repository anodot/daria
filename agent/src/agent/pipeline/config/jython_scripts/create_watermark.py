global sdc

try:
    sdc.importLock()
    import time
    import os
    import sys

    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import requests
finally:
    sdc.importUnlock()

slept = False
for record in sdc.records:
    if record.attributes['sdc.event.type'] == 'finished-file':
        if not slept:
            # sleep a little bit to let the pipeline finish processing and sending file data
            time.sleep(int(sdc.userParams['SLEEP_TIME']))
            slept = True
        res = requests.get(sdc.userParams['PIPELINE_OFFSET_URL'])
        res.raise_for_status()
        record.value['watermark'] = float(res.json()) + float(sdc.userParams['BUCKET_SIZE_IN_SECONDS'])
        record.value['schemaId'] = sdc.userParams['SCHEMA_ID']
        # send monitoring metric with file_processed 1 and now() - watermark
        sdc.output.write(record)
