global sdc, output, error


def extract_value(obj, path):
    for part in path.split('/'):
        obj = obj.get(part)
        if not obj:
            return None
    # todo how could it be?
    if not obj:
        return None
    return obj


def replace_illegal_chars(s):
    return s.replace('[\. \<]+', '_')


def get_dimensions(record):
    dimensions = {}
    for dimension, name in sdc.userParams['DIMENSIONS'].items():
        dimension = extract_value(record.value, replace_illegal_chars(dimension))
        if not dimension:
            continue
        dimension = str(dimension).strip()
        if dimension == '':
            continue
        name = replace_illegal_chars(name).replace('[\/]+', '_')
        dimensions[name] = dimension

    for header_attribute in sdc.userParams['HEADER_ATTRIBUTES']:
        attribute_value = record.attributes[header_attribute]
        if not attribute_value:
            continue
        attribute_value = str(attribute_value).strip()
        if attribute_value == '':
            continue
        dimensions[replace_illegal_chars(header_attribute)] = replace_illegal_chars(attribute_value)

    return dimensions


def get_measurements(record):
    measurements = {}
    for value_column, name in sdc.userParams['MEASUREMENTS'].items():
        value = extract_value(record, value_column)
        if not value:
            continue
        # we can't convert to float here because we will loose precision
        # it should be converted in a separate stage
        measurements[name] = value
    if sdc.userParams['COUNT_RECORDS']:
        measurements[sdc.userParams['COUNT_RECORDS_MEASUREMENT_NAME']] = 1
    return measurements


def main():
    i = -1
    for record in sdc.records:
        i += 1
        try:
            timestamp = extract_value(record.value, sdc.userParams['TIMESTAMP_COLUMN'])
            if not timestamp:
                continue
            measurements = get_measurements(record.value)
            if not measurements:
                continue
            new_record = sdc.createRecord(str(i))
            new_record.value = {
                'timestamp': timestamp,
                'dimensions': get_dimensions(record),
                'measurements': measurements,
                'schemaId': '${SCHEMA_ID}',
            }
            output.write(new_record)
        except Exception as e:
            error.write(record, str(e))


main()