global sdc, records

query = sdc.userParams['QUERY'].replace(
    sdc.userParams['LAST_TIMESTAMP_TEMPLATE'], str(records[0].value['last_timestamp'])
)

recs = []
for record in sdc.records:
    try:
        del record.value['last_timestamp']
        if record.value:
            recs.append(record)
    except Exception as e:
        sdc.error.write(record, str(e))

sent_query = False
for record in recs:
    rec = sdc.createRecord('record')
    rec.value = sdc.createMap(True)
    for key in record.value:
      rec.value[key] = record.value[key]
    sdc.output.write(rec)
if recs and not sent_query and sdc.userParams['LOGGING_OF_QUERIES_ENABLED']:
    rec = sdc.createRecord('record query')
    rec.value = sdc.createMap(True)
    rec.value['query'] = query
    sdc.output.write(rec)
    sent_query = True
