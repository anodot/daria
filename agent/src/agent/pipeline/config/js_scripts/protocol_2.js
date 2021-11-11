TARGET_TYPES = ['counter', 'gauge', 'running_counter']

function get_value(path, value) {
  var path_parts = path.split('/')
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

function metric_to_string(dimensions) {
  var str = '';
    for (var p in dimensions) {
        if (dimensions.hasOwnProperty(p)) {
            str += p + ':' + dimensions[p] + ',';
        }
    }
    return str;
}

function get_running_counter_value(metric_properties, curr_value, time) {
  var metric = metric_to_string(metric_properties)
  if (state['metrics'][metric] == null) {
    state['metrics'][metric] = {'val': curr_value, 'time': time}
    return null;
  }
  var counter_val = curr_value - state['metrics'][metric]['val']
  if (counter_val < 0) {
    state['metrics'][metric] = null
    return null;
  }
  state['metrics'][metric]['val'] = curr_value
  var prev_time = state['metrics'][metric]['time']
  state['metrics'][metric]['time'] = time
  return counter_val / (time - prev_time)
}

function get_target_type_value(target_type_property, record) {
  if (TARGET_TYPES.indexOf(target_type_property) < 0) {
    if (TARGET_TYPES.indexOf(record[target_type_property]) < 0) {
      throw 'Target type property ' + target_type_property + ' should be counter, gauge or running_counter'
    }
    return get_value(target_type_property, record)
  }
  return target_type_property
}

for(var i = 0; i < records.length; i++) {
  try {
	var timestamp = get_value(state['TIMESTAMP_COLUMN'], records[i].value)

    var properties = {}
    for (var dimension_path in state['DIMENSIONS']) {
      var dim_val = get_value(dimension_path, records[i].value);
      dim_val = String(dim_val).trim();
      if (dim_val !== '' && dim_val !== 'null') {
        properties[state['DIMENSIONS'][dimension_path].replace(/[\.\s\/]+/g, '_')] = dim_val.replace(/[\.\s]+/g, '_')
      }
    }

    var j = 0;
    for (var measurement_path in state['MEASUREMENTS']) {
      var values_array = [records[i].value]
      if (state['VALUES_ARRAY_PATH'].length > 0) {
        values_array = get_value(state['VALUES_ARRAY_PATH'], records[i].value)
      }
      for (var l = 0; l < values_array.length; l++) {
        if (state['STATIC_WHAT']) {
          properties['what'] = state['MEASUREMENTS'][measurement_path].replace(/[\.\s]+/g, '_');
          properties['target_type'] = state['TARGET_TYPES'][j];
        } else {
          meas_name = get_value(state['MEASUREMENTS'][measurement_path], values_array[l])
          if (state['VALUES_ARRAY_FILTER'].length > 0 && state['VALUES_ARRAY_FILTER'].indexOf(meas_name) < 0) {
            continue;
          }
          properties['what'] = String(meas_name).replace(/[\.\s]+/g, '_');
          properties['target_type'] = get_target_type_value(state['TARGET_TYPES'][j], values_array[l]);
        }

        var newRecord = sdcFunctions.createRecord(records[i].sourceId + ':' + i);
        var value = get_value(measurement_path, values_array[l])
        if (properties['target_type'] == 'running_counter') {
          properties['target_type'] = 'gauge';
          value = get_running_counter_value(properties, value, timestamp);
        }

        if (value === null || value === '') {
            continue;
        }
        newRecord.value = {'timestamp' : timestamp,
                           'properties' : properties,
                           'value': value};
        output.write(newRecord);
      }
      j++;
    }
    if (state['COUNT_RECORDS']) {
      var newRecord = sdcFunctions.createRecord(records[i].sourceId + ':' + i);
      properties['what'] = state['COUNT_RECORDS_MEASUREMENT_NAME'];
      properties['target_type'] = 'counter';
      newRecord.value = {'timestamp' : timestamp,
                         'properties' : properties,
                         'value': 1};
      output.write(newRecord);
    }

    // output.write(records[i]);
  } catch (e) {
    // Send record to error
    error.write(records[i], e);
  }
}