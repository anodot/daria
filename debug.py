import json

import requests

from agent import cli, source, destination, pipeline, streamsets, di
from agent.modules import db

di.init()

s = source.repository.get_by_name('solarwinds')
s.config['new'] = 'anton'
ss = source.repository.get_by_name('solarwinds')
t = 1

# cli.source.create(["-f", "/Users/antonzelenin/Workspace/daria/agent/tests/input_files/solarwinds_sources.json"])

# # session = requests.Session()
# # session.auth = ('Admin', 'admin')
#
# # res = session.get(
# #     'https://10.0.94.226:17778/SolarWinds/InformationService/v3/Json/Query?query=SELECT+Uri+FROM+Orion.Pollers+ORDER+BY+PollerID+WITH+ROWS+1+TO+3+WITH+TOTALROWS',
# #     verify=False
# # )
# t = 1
# # cli.source.edit(["test_mongo"])
# # cli.destination()
# # cli.pipeline.create()
# # cli.streamsets.delete(["asdfa"])

# SELECT+TOP+1000+NodeID,+DateTime,+Archive,+MinLoad,+MaxLoad,+AvgLoad,+TotalMemory,+MinMemoryUsed,+MaxMemoryUsed,+AvgMemoryUsed,+AvgPercentMemoryUsed+FROM+Orion.CPULoad
# import time
# import traceback
# import requests
#
# from datetime import datetime, timedelta
#
# # single threaded - no entityName because we need only one offset
# entityName = ''
# DATEFORMAT = '%Y-%m-%dT%H:%M:%SZ'
#
# # because user specifies the interval in minutes
# interval = timedelta(seconds=60 * 60)
# delay = timedelta(minutes=0)
# days_to_backfill = timedelta(days=10)
#
#
# # Jython converts datetime objects to java.sql.Timestamp when assigning it to a variable
# def date_from_str(date):
#     return datetime.strptime(date, DATEFORMAT)
#
#
# def date_to_str(date):
#     return date.strftime(DATEFORMAT)
#
#
# offset = date_to_str(datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - days_to_backfill)
#
# N_REQUESTS_TRIES = 3
#
# while True:
#     start_time = time.time()
#     try:
#         end_time = date_to_str(date_from_str(offset) + interval)
#         latest_date = date_to_str(datetime.utcnow().replace(second=0, microsecond=0) - delay)
#         sleep = (date_from_str(end_time) - date_from_str(latest_date)).total_seconds() - (time.time() - start_time)
#         if sleep > 0:
#             time.sleep(sleep)
#
#         for i in range(1, N_REQUESTS_TRIES + 1):
#             session = requests.Session()
#             session.auth = ('Admin', 'admin')
#             res = session.get(
#                 'https://10.0.94.226:17778/' + 'SolarWinds/InformationService/v3/Json/Query',
#                 params={'query': 'SELECT Uri FROM Orion.Pollers ORDER BY PollerID WITH ROWS 1 TO 3 WITH TOTALROWS'},
#                 verify=False, timeout=180
#             )
#             res.raise_for_status()
#             break
#
#         data = res.json()
#
#         # send batch and save offset
#         offset = end_time
#     except Exception as e:
#         raise


# with open('/Users/antonzelenin/Workspace/daria/dummy_destination/data/solarwinds_data_example.json') as f:
#     r = json.load(f)
#     t = 1
