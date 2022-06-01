global sdc, output

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
    # we need one header and at least one row
    if len(sdc.records) <= 1:
        return

    data = []
    # headers is a dict {"0": "column_name"}
    headers = sdc.records[0].value
    for i in range(1, len(sdc.records)):
        # record value is a dict {"0": "value"}
        obj = {headers[j]: val for j, val in sdc.records[i].value.items()}
        data.append(obj)

    if data:
        record = sdc.createRecord('record created')
        record.value = data
        output.write(record)


main()
