function merge_two_objects(obj1, obj2) {
    var new_val = {}
    for (var attrname in obj1) { new_val[attrname] = obj1[attrname]; }
    for (var attrname in obj2) { new_val[attrname] = obj2[attrname]; }
    return new_val
}

function get_value(path, value) {
    path_parts = path.split('/')
    for (var k = 0; k < path_parts.length; k++) {
        value = value[path_parts[k]]
    }
    return value
}

for (var i = 0; i < records.length; i++) {

    if (state['VALUES_ARRAY_PATH']) {
        var items = get_value(state['VALUES_ARRAY_PATH'], records[i].value)

        for (var l = 0; l < items.length; l++) {
            var newRecord = sdcFunctions.createRecord(i + '_' + l);
            newRecord.value = merge_two_objects(records[i].value, items[l])
            output.write(newRecord)
        }

    } else {
        output.write(records[i])
    }

}