global sdc

try:
    sdc.importLock()
    import sys
    import os
    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import requests
    import traceback
finally:
    sdc.importUnlock()


def main():
    url = sdc.userParams['URL'] + '/api/v1/export?match[]={__name__="not_existing_dsger43"}'
    session = requests.Session()
    if sdc.userParams['USERNAME']:
        session.auth = (sdc.userParams['USERNAME'], sdc.userParams['PASSWORD'])
    try:
        res = session.get(url, verify=sdc.userParams['VERIFY_SSL'], timeout=sdc.userParams['REQUEST_TIMEOUT'])
        res.raise_for_status()
    except Exception as e:
        sdc.log.error(str(e))
        sdc.log.error(traceback.format_exc())
        raise


main()
