import requests

global sdc, output, error

try:
    sdc.importLock()
    import re
    import time
finally:
    sdc.importUnlock()


def _start_rollup():
    pass


def _end_rollup():
    pass


# todo rollup end might take several minutes so make sure to wait enough
# todo rollup can fail on the end call, in this case we must try one more time?
def main():
    _start_rollup()
    timestamp = time.time()
    rows = {}
    base = {
        "type": "SITE",
        "rollupId": 27,
        "timestamp": timestamp,
        "bulkSerNumber": 1,
    }
    for record in sdc.records:
        try:
            rows[record.value[sdc.userParams['ID_KEY']]] = {
                'geoLocation': {
                    'lat': record.value[sdc.userParams['LAT_KEY']],
                    'lon': record.value[sdc.userParams['LON_KEY']]
                },
                'status': record.value[sdc.userParams['STATUS_KEY']],
                'regionId': record.value[sdc.userParams['STATUS_KEY']],
                'name': record.value[sdc.userParams['ID_KEY']],
                'id': record.value[sdc.userParams['ID_KEY']],
            }
        except Exception as e:
            error.write(record, str(e))
    base['rows'] = rows
    base['numberOfRows'] = len(rows)

    res = requests.post('some-topology.com/bla')
    res.raise_for_status()


main()
