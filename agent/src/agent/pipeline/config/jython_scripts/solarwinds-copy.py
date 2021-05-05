import time
import traceback
import requests

from datetime import datetime, timedelta

# single threaded - no entityName because we need only one offset
entityName = ''
DATEFORMAT = '%Y-%m-%dT%H:%M:%SZ'

# because user specifies the interval in minutes
interval = timedelta(seconds=60 * 60)
delay = timedelta(minutes=0)
days_to_backfill = timedelta(days=10)


# Jython converts datetime objects to java.sql.Timestamp when assigning it to a variable
def date_from_str(date):
    return datetime.strptime(date, DATEFORMAT)


def date_to_str(date):
    return date.strftime(DATEFORMAT)


offset = date_to_str(datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - days_to_backfill)

N_REQUESTS_TRIES = 3

while True:
    start_time = time.time()
    try:
        end_time = date_to_str(date_from_str(offset) + interval)
        latest_date = date_to_str(datetime.utcnow().replace(second=0, microsecond=0) - delay)
        sleep = (date_from_str(end_time) - date_from_str(latest_date)).total_seconds() - (time.time() - start_time)
        if sleep > 0:
            time.sleep(sleep)

        for i in range(1, N_REQUESTS_TRIES + 1):
            session = requests.Session()
            session.auth = ('Admin', 'admin')
            res = requests.get(
                'https://10.0.94.226:17778/' + '/SolarWinds/InformationService/v3/Json/Query',
                params={'query': 'SELECT Uri FROM Orion.Pollers ORDER BY PollerID WITH ROWS 1 TO 3 WITH TOTALROWS'},
                verify=False, timeout=180
            )
            res.raise_for_status()
            break

        data = res.json()

        # send batch and save offset
        offset = end_time
    except Exception as e:
        raise
