global sdc, output, error


def get_properties(record):
    props = {k: v for k, v in record.value.items() if k not in ['timestamp', '__name__', record.value['what']]}
    props['target_type'] = 'gauge'
    return props


def main():
    for i, record in enumerate(sdc.records):
        try:
            new_record = sdc.createRecord(str(i))
            new_record.value = {
                'timestamp': record.value['timestamp'],
                'properties': get_properties(record),
                'value': record.value[record.value['what']],
            }
            output.write(new_record)
        except Exception as e:
            error.write(record, str(e))


main()
