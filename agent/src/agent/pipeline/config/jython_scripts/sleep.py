global sdc

try:
    sdc.importLock()
    import time
finally:
    sdc.importUnlock()

slept = False
for record in sdc.records:
    if record.attributes['sdc.event.type'] == 'finished-file' and not slept:
        time.sleep(sdc.userParams['SLEEP_TIME'])
        slept = True
    sdc.output.write(record)
