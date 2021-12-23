global sdc

try:
    sdc.importLock()
    import sys
    import os
    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import urllib.parse
    import requests
    import traceback
finally:
    sdc.importUnlock()


def main():
    session = requests.Session()
    session.auth = (sdc.userParams['API_USER'], sdc.userParams['API_PASSWORD'])
    try:
        res = session.get( sdc.userParams['DEVICES_URL'], verify=False)
        res.raise_for_status()
    except Exception as e:
        sdc.log.error(str(e))
        sdc.log.error(traceback.format_exc())
        raise


main()
