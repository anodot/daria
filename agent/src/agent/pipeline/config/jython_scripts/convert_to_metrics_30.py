global sdc, output, error

try:
    sdc.importLock()
    import re
finally:
    sdc.importUnlock()


def extract_value(obj, path):
    for part in path.split('/'):
        obj = obj[int(part)]if type(obj) == list else obj.get(part, None)
    return obj


def replace_illegal_chars(value):
    if type(value).__name__ not in ['unicode', 'str']:
        value = str(value)
    value = value.strip().replace(".", "_")
    return re.sub('\s+', '_', value)


def get_dimensions(record):
    dimensions = {}
    for dimension_path, name in sdc.userParams['DIMENSIONS'].items():
        dimension_value = extract_value(record.value, dimension_path)
        if not dimension_value:
            continue
        dimension_value = replace_illegal_chars(dimension_value)
        if dimension_value == '':
            continue
        name = replace_illegal_chars(name).replace('[\/]+', '_')
        dimensions[name] = dimension_value

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


def get_dynamic_tags(record):
    tags = {}
    for tag_name, tag_path in sdc.userParams['DYNAMIC_TAGS'].items():
        try:
            tag_value = extract_value(record.value, tag_path)
            if not tag_value:
                continue
            tag_value = str(tag_value).strip()
            if tag_value == '':
                continue
            tags[replace_illegal_chars(tag_name)] = [replace_illegal_chars(tag_value)]
        except Exception as e:
            sdc.log.error("Can't retrieve tag: " + str(e))
    return tags or None


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
                'tags': get_dynamic_tags(record),
            }
            output.write(new_record)
        except Exception as e:
            error.write(record, str(e))


'%TRANSFORM_SCRIPT_PLACEHOLDER%'
main()
