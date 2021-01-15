for (let i = 0; i < records.length; i++) {
    let dimensions = {};
    for (let j = 0; j < state['DIMENSIONS'].length; j++) {
        let dimension = records[i].value[state['DIMENSIONS'][j]]
        let dimension_name = state['DIMENSIONS_NAMES'][j].replace(/[\. \/]+/g, '_')
        if (dimension !== null && dimension !== '') {
            dimensions[dimension_name] = String(dimension).replace(/[\. ]+/g, '_')
        }
    }

    try {
        let measurements = {}
        for (let j = 0; j < state['VALUES_COLUMNS'].length; j++) {
            let measurement = '';
            if (state['STATIC_WHAT']) {
                measurement = state['MEASUREMENT_NAMES'][j].replace(/[\. ]+/g, '_');
            } else {
                let meas_name = records[i].value[state['MEASUREMENT_NAMES'][j]]
                if (typeof meas_name !== 'string') {
                    throw state['MEASUREMENT_NAMES'][j] + ' property should be string instead of ' + (typeof meas_name)
                }
                measurement = meas_name.replace(/[\. ]+/g, '_');
            }
            measurements[measurement] = records[i].value[state['VALUES_COLUMNS'][j]];
        }
        if (state['COUNT_RECORDS']) {
            // todo remember about properties['target_type'] = 'counter';
            if (records[i].value[state['TIMESTAMP_COLUMN']] !== null) {
                measurements[state['COUNT_RECORDS_MEASUREMENT_NAME']] = 1;
            }
        }
        let newRecord = sdcFunctions.createRecord(records[i].sourceId + ':' + i);
            newRecord.value = {
                'timestamp': records[i].value[state['TIMESTAMP_COLUMN']],
                'dimensions': dimensions,
                'measurements': measurements,
                'schemaId': "${SCHEMA_ID}"
            };
            output.write(newRecord);
    } catch (e) {
        error.write(records[i], e);
    }
}
