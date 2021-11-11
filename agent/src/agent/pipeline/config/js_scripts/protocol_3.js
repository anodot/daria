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
        var dimension_value = extract_value(record.value, replace_illegal_chars(dimension_path))
        dimension_value = String(dimension_value).trim()
        if (dimension_value === '' || dimension_value === 'null') {
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
            'schemaId': "${SCHEMA_ID}"
        };
        output.write(newRecord);
    } catch (e) {
        error.write(records[i], e);
    }
}

if (records.length > 0 && extract_value(records[0].value, state['TIMESTAMP_COLUMN'])) {
  event = sdc.createEvent('interval processed', 1);
  event.value = {
    'watermark': records[0].value['last_timestamp'] + state['INTERVAL'] ,
  };
  sdc.toEvent(event);
}
