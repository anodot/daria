for (var i = 0; i < records.length; i++) {
    var dimensions = {};
    for (var j = 0; j < state['DIMENSIONS'].length; j++) {
        var dimension = records[i].value[state['DIMENSIONS'][j]]
        var dimension_name = state['DIMENSIONS_NAMES'][j].replace(/[\. \/]+/g, '_')
        if (dimension !== null && dimension !== '') {
            dimensions[dimension_name] = String(dimension).replace(/[\. ]+/g, '_')
        }
    }

    try {
        if (records[i].value[state['TIMESTAMP_COLUMN']] === null) {
            continue;
        }
        var measurements = {}
        for (var j = 0; j < state['VALUES_COLUMNS'].length; j++) {
            var value = records[i].value[state['VALUES_COLUMNS'][j]];
            if (value === null || value === '') {
              continue;
            }
            var measurement = '';
            if (state['STATIC_WHAT']) {
                measurement = state['MEASUREMENT_NAMES'][j].replace(/[\. ]+/g, '_');
            } else {
                var meas_name = records[i].value[state['MEASUREMENT_NAMES'][j]]
                if (typeof meas_name !== 'string') {
                    throw state['MEASUREMENT_NAMES'][j] + ' property should be string instead of ' + (typeof meas_name)
                }
                measurement = meas_name.replace(/[\. ]+/g, '_');
            }
            if (typeof value === 'string' || value instanceof String) {
                value = parseFloat(value)
            }
            measurements[measurement] = value;
        }
        if (state['COUNT_RECORDS']) {
            measurements[state['COUNT_RECORDS_MEASUREMENT_NAME']] = 1;
        }
        var newRecord = sdcFunctions.createRecord(records[i].sourceId + ':' + i);
        newRecord.value = {
             'timestamp': records[i].value[state['TIMESTAMP_COLUMN']],
             'dimensions': dimensions,
             'measurements': measurements,
             'schemaId': "${SCHEMA_ID}",
         };
         output.write(newRecord);
    } catch (e) {
        error.write(records[i], e);
    }
}

if (records.length > 0 && records[0].value[state['TIMESTAMP_COLUMN']] !== null) {
  var event = sdc.createEvent('interval processed', 1);
  event.value = {
    'watermark': records[0].value['last_timestamp'] + state['INTERVAL'] ,
  };
  sdc.toEvent(event);
}