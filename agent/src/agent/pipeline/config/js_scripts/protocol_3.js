function get_value(path, value) {
  path_parts = path.split('/')
  for (var k = 0; k < path_parts.length; k++) {
    value = value[path_parts[k]]
    if (value === null) {
      return null;
    }
  }
  if (value === null) {
    return 'NULL';
  }
  return value
}


function replace_illegal_chars(str) {
    return str.replace(/[\. ]+/g, '_')
}

function get_measurement_name(record, value_idx) {
    // if (!state['STATIC_WHAT']) {
    //     var meas_name = get_value(state['MEASUREMENT_NAMES'][value_idx], record)
    //     if (typeof meas_name !== 'string') {
    //         throw state['MEASUREMENT_NAMES'][value_idx] + ' property should be string instead of ' + (typeof meas_name)
    //     }
    //     return replace_illegal_chars(meas_name);
    // }
    return state['MEASUREMENT_NAMES'][value_idx]
}

function get_dimensions(record) {
    var dimensions = {};
    for (var j = 0; j < state['DIMENSIONS'].length; j++) {
        var dimension = get_value(state['DIMENSIONS'][j], record)
        if (dimension === null) {
            continue;
        }
        dimension = String(dimension).trim()
        if (dimension === '') {
            continue;
        }
        var dimension_name = replace_illegal_chars(state['DIMENSIONS_NAMES'][j]).replace(/[\/]+/g, '_')
        dimensions[dimension_name] = replace_illegal_chars(dimension)

    }
    return dimensions
}

function get_measurements(record) {
    var measurements = {}
    for (var j = 0; j < state['VALUES_COLUMNS'].length; j++) {
        var value = get_value(state['VALUES_COLUMNS'][j], record);
        if (value === null || value === '' || isNaN(value)) {
            continue;
        }
        if (typeof value === 'string' || value instanceof String) {
            value = parseFloat(value)
        }
        var measurement = get_measurement_name(record, j);

        measurements[measurement] = value;
    }
    if (state['COUNT_RECORDS']) {
        measurements[state['COUNT_RECORDS_MEASUREMENT_NAME']] = 1;
    }
    return measurements
}


for (var i = 0; i < records.length; i++) {

    try {
        var timestamp = get_value(state['TIMESTAMP_COLUMN'], records[i].value)
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
            'dimensions': get_dimensions(records[i].value),
            'measurements': measurements,
            'schemaId': "${SCHEMA_ID}"
        };
        output.write(newRecord);
    } catch (e) {
        error.write(records[i], e);
    }
}

if (records.length > 0 && get_value(state['TIMESTAMP_COLUMN'], records[0].value)) {
  event = sdc.createEvent('interval processed', 1);
  event.value = {
    'watermark': records[0].value['last_timestamp'] + state['INTERVAL'] ,
  };
  sdc.toEvent(event);
}
