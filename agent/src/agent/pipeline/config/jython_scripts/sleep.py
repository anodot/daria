global sdc

try:
    sdc.importLock()
    import time
finally:
    sdc.importUnlock()

time.sleep(sdc.userParams['SLEEP_TIME'])

for record in sdc.records:
    sdc.output.write(record)