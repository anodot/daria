global sdc, output, error

try:
    sdc.importLock()
    import sys
    import os

    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import requests
finally:
    sdc.importUnlock()

entityName = ''


def main():
    for record in sdc.records:
        res = requests.post(sdc.userParams['TOPOLOGY_TRANSFORM_RECORDS_URL'], json=record.value)
        res.raise_for_status()

        record = sdc.createRecord('record created')
        record.value = res.json()
        output.write(record)


main()
