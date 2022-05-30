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
    data = []
    if len(sdc.records) > 1:
        headers = sdc.records[0].value
        for i in range(1, len(sdc.records)):
            obj = {headers[j]: val for j, val in sdc.records[i].value.items()}
            data.append(obj)

    record = sdc.createRecord('record created')
    record.value = data
    output.write(record)


main()
