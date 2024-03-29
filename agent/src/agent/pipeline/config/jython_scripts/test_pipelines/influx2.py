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
    session = requests.Session()
    session.headers = sdc.userParams['HEADERS']
    try:
        res = session.get(sdc.userParams['URL'], timeout=sdc.userParams['TIMEOUT'])
        res.raise_for_status()
        bucket_list = [bucket['name'] for bucket in res.json()['buckets']]

        if sdc.userParams['BUCKET'] not in bucket_list:
            raise Exception('Bucket %s not found. Please check your input again' % sdc.userParams['BUCKET'])
    except Exception as e:
        sdc.log.error(str(e))
        sdc.log.error(traceback.format_exc())
        raise


main()
