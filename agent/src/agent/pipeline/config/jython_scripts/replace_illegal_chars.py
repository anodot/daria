global sdc

try:
    sdc.importLock()
    import re
finally:
    sdc.importUnlock()


def replace_illegal_chars(value):
    if type(value).__name__ not in ['unicode', 'str']:
        value = str(value)
    value = value.strip().replace(".", "_")
    return re.sub('\s+', '_', value)


def replace_all(record, key):
    for k, v in record.value[key].items():
        new_k = replace_illegal_chars(k)
        new_v = replace_illegal_chars(v)
        if new_k != k or new_v != v:
            record.value[key][new_k] = new_v
        if new_k != k:
            record.value[key].pop(k)


def replace_keys(record, key):
    for k, v in record.value[key].items():
        new_k = replace_illegal_chars(k)
        if new_k != k:
            record.value[key][new_k] = v
            record.value[key].pop(k)


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
            for k, vals in record.value['tags'].items():
                record.value['tags'][k] = [replace_illegal_chars(v) for v in vals]
        sdc.output.write(record)


main()
