
global sdc, output, error

try:
    sdc.importLock()
    import re
    import time
    import sys
    import os
    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    from anodot_api_client import AnodotApiClient
finally:
    sdc.importUnlock()


class TopologyDataLoad:
    def __init__(self, client: AnodotApiClient):
        self.api_client = client

    def __enter__(self):
        res = self.api_client.post(
            sdc.userParams['LOAD_START_URL']
        )
        res.raise_for_status()
        return res.json()['rollupid']

    def __exit__(self, exc_type, exc_value, exc_traceback):
        _clean()


# todo rollup end might take several minutes so make sure to wait enough
# todo rollup can fail on the end call, in this case we must try one more time?
def main():
    client = AnodotApiClient(
        sdc.state, sdc.userParams['REFRESH_TOKEN_URL'], sdc.userParams['ACCESS_TOKEN'], sdc.userParams['PROXIES']
    )
    with TopologyDataLoad(client) as load_id:
        # timestamp = time.time()
        rows = {}
        base = {
            "type": "SITE",
            "rollupId": load_id,
            # it's optional, do we need it?
            # "timestamp": timestamp,
            "bulkSerNumber": 1,
        }
        # todo batch must be 500
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
