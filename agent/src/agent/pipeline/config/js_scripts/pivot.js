function merge_two_objects(obj1, obj2) {
    var new_val = {}
    for (var attrname in obj1) { new_val[attrname] = obj1[attrname]; }
    for (var attrname in obj2) { new_val[attrname] = obj2[attrname]; }
    return new_val
}

function extract_value(object, path) {
    path_parts = path.split('/')
    for (var k = 0; k < path_parts.length; k++) {
        object = object[path_parts[k]]
    }
    return object
}
for (var i = 0; i < records.length; i++) {
    if (state['SELECTED_PARTITIONS'].size() && !state['SELECTED_PARTITIONS'][+records[i].attributes.partition]){
        continue;
    }
    if (state['VALUES_ARRAY_PATH']) {
        var items = extract_value(records[i].value, state['VALUES_ARRAY_PATH'])

        for (var l = 0; l < items.length; l++) {
            var newRecord = sdcFunctions.createRecord(i + '_' + l);
            newRecord.value = merge_two_objects(records[i].value, items[l])
            output.write(newRecord)
        }

    } else {
        output.write(records[i])
    }

}
