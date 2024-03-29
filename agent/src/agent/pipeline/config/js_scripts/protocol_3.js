function extract_value(object, path) {
  path_parts = path.split('/')
  for (var k = 0; k < path_parts.length; k++) {
    object = object[path_parts[k]]
    if (object === null) {
      return null;
    }
  }
  if (object === null) {
    return 'NULL';
  }
  return object
}


function replace_illegal_chars(str) {
    return str.replace(/[\. \<]+/g, '_')
}

function get_dimensions(record) {
    var dimensions = {};
    for (var dimension_path in state['DIMENSIONS']) {
        var dimension_value = extract_value(record.value, dimension_path)
        if (dimension_value === null) {
            continue;
        }
        dimension_value = String(dimension_value).trim()
        if (dimension_value === '') {
            continue;
        }
        var dimension_name = replace_illegal_chars(state['DIMENSIONS'][dimension_path]).replace(/[\/]+/g, '_')
        dimensions[dimension_name] = replace_illegal_chars(dimension_value)
    }

    for (var k = 0; k < state['HEADER_ATTRIBUTES'].length; k++) {
        var attribute_value = record.attributes[state['HEADER_ATTRIBUTES'][k]]
        if (attribute_value === null) {
            continue;
        }
        attribute_value = String(attribute_value).trim()
        if (attribute_value === '') {
            continue;
        }
        dimensions[replace_illegal_chars(state['HEADER_ATTRIBUTES'][k])] = replace_illegal_chars(attribute_value)
    }
    return dimensions
}

function get_measurements(record) {
    var measurements = {}
    for (var measurement_path in state['MEASUREMENTS']) {
        var value = extract_value(record, measurement_path);
        if (value === null || value === '' || isNaN(value)) {
            continue;
        }
        if (typeof value === 'string' || value instanceof String) {
            value = parseFloat(value)
        }
        measurements[state['MEASUREMENTS'][measurement_path]] = value;
    }
    if (state['COUNT_RECORDS']) {
        measurements[state['COUNT_RECORDS_MEASUREMENT_NAME']] = 1;
    }
    return measurements
}

function get_dynamic_tags(record) {
    var tags = {}
    for (var tag_name in state['DYNAMIC_TAGS']) {
        var value_path = state['DYNAMIC_TAGS'][tag_name];
        var tag_value = extract_value(record.value, value_path);
        if (tag_value === null) {
            continue;
        }
        tag_value = String(tag_value).trim()
        if (tag_value === '') {
            continue;
        }
        var tag_correct_name = replace_illegal_chars(tag_name).replace(/[\/]+/g, '_')
        tags[tag_correct_name] = [replace_illegal_chars(tag_value)]
    }
    return tags
}

function last_timestamp_only(record) {
    var record_keys = [];
    for (var key in record) {
        record_keys.push(key)
    }
    return (record_keys.length === 1 && record_keys[0] === 'last_timestamp');
}

'%TRANSFORM_SCRIPT_PLACEHOLDER%'

if (records.length === 1 && last_timestamp_only(records[0].value)) {
    var timestamp_from = records[0].value['last_timestamp']
    var timestamp_to = records[0].value['last_timestamp'] + state['INTERVAL']
    sdc.log.info("No data from " + timestamp_from + " to " + timestamp_to)
} else {
    for (var i = 0; i < records.length; i++) {
        try {
            var timestamp = extract_value(records[i].value, state['TIMESTAMP_COLUMN'])
            if (timestamp === null) {
                continue;
            }
            var measurements = get_measurements(records[i].value)
            if (JSON.stringify(measurements) === JSON.stringify({})) {
                continue;
            }
            var newRecord = sdcFunctions.createRecord(i);
            newRecord.value = {
                'timestamp': timestamp,
                'dimensions': get_dimensions(records[i]),
                'measurements': measurements,
                'schemaId': "${SCHEMA_ID}",
                'tags': get_dynamic_tags(records[i]),
            };
            if (records[i].value['__tags'] !== null) {
                newRecord.value['tags'] = records[i].value['__tags']
            }
            output.write(newRecord);
        } catch (e) {
            error.write(records[i], e);
        }
    }
}

if (records.length > 0 && (state['SEND_WATERMARK_IF_NO_DATA'] === 'True' || extract_value(records[0].value, state['TIMESTAMP_COLUMN']))) {
  event = sdc.createEvent('interval processed', 1);
  event.value = {
    'watermark': records[0].value['last_timestamp'] + state['INTERVAL'],
  };
  sdc.toEvent(event);
}
