for (var i = 0; i < records.length; i++) {
    re = /(\([^)]+\))[,]*/g;
    var tags;
    do {
        tags = re.exec(records[i].value['tags'])
        if (tags) {
            if (records[i].value['__tags'] === null) {
                records[i].value['__tags'] = {}
            }
            r = /\(\'([^']+)\'[^']+\'([^']+)\'/g
            res = r.exec(tags[1])
            tag = res[1]
            val = res[2]
            records[i].value['__tags'][tag] = [val]
        }
    } while (tags)
}