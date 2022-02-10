global sdc, output, error


def get_properties(record):
    props = {k: v for k, v in record.value.items() if k not in ['timestamp', '__name__', '__value', 'last_timestamp']}
    props['target_type'] = 'gauge'
    props['what'] = record.value['__name__']
    return props


def main():
    for i, record in enumerate(sdc.records):
        try:
            new_record = sdc.createRecord(str(i))
            new_record.value = {
                'timestamp': record.value['timestamp'],
                'properties': get_properties(record),
                'value': record.value['__value'],
            }
            output.write(new_record)
        except Exception as e:
            error.write(record, str(e))


main()
