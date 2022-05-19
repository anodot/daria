global sdc, error

try:
    sdc.importLock()
    import re
    import time
    import sys
    import os

    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    from anodot_api_client import AnodotApiClient, AnodotUrlBuilder
finally:
    sdc.importUnlock()


class TopologyDataLoad:
    def __init__(self, client):
        self.api_client = client
        self.rollup_id = None

    def __enter__(self):
        res = self.api_client.start_topology_data_load()
        if res.status_code != 200:
            sdc.log.error('Error starting rollup')
            sdc.log.error(str(res.json()))
        res.raise_for_status()
        self.rollup_id = str(res.json()['rollupId'])
        return self.rollup_id

    def __exit__(self, exc_type, exc_value, exc_traceback):
        res = self.api_client.end_topology_data_load(self.rollup_id)
        if res.status_code != 200:
            sdc.log.error('Error ending rollup')
            sdc.log.error(str(res.json()))
        res.raise_for_status()


# todo ?
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def main():
    client_ = AnodotApiClient(
        sdc.state, sdc.userParams['ANODOT_URL'], sdc.userParams['ACCESS_TOKEN'], sdc.userParams['PROXIES']
    )
    with TopologyDataLoad(client_) as rollup_id:
        for record in sdc.records:
            for entity_type, entities in record.value.items():
                # timestamp = time.time()
                base = {
                    "type": entity_type,
                    "rollupId": rollup_id,
                    # it's optional, do we need it?
                    # "timestamp": timestamp,
                    "bulkSerNumber": 1,
                }
                for i, chunk in enumerate(chunks(entities, 500)):
                    data = base.copy()
                    rows = {}
                    for entity in chunk:
                        try:
                            rows[entity[id]] = entity
                        except Exception as e:
                            error.write(record, str(e))

                    data['rows'] = rows
                    data['numberOfRows'] = len(rows)
                    # i starts from 0 and bulkSerNumber starts from 1
                    data['bulkSerNumber'] = i + 1

                    # todo what if it fails?
                    res = client_.send_topology_data(data, rollup_id)
                    if res.status_code != 200:
                        sdc.log.error('ERROR SENDING DATA')
                        sdc.log.error(str(res.json()))
                    res.raise_for_status()


main()
