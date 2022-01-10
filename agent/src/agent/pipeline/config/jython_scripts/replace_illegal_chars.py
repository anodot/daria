global sdc

try:
    sdc.importLock()
    import re
finally:
    sdc.importUnlock()


def replace_illegal_chars(value):
    value = str(value).strip().replace(".", "_")
    return re.sub('\s+', '_', value)


def replace_all(record, key):
    for k, v in record.value[key]:
        record.value[key][replace_illegal_chars(k)] = replace_illegal_chars(v)


def replace_keys(record, key):
    for k, v in record.value[key]:
        record.value[key][replace_illegal_chars(k)] = v


def main():
    for record in sdc.records:
        if 'properties' in record.value:
            replace_all(record, 'properties')
        if 'dimensions' in record.value:
            replace_all(record, 'dimensions')
        if 'measurements' in record.value:
            replace_keys(record, 'measurements')
        if 'tags' in record.value:
            replace_keys(record, 'tags')
        sdc.output.write(record)


main()
