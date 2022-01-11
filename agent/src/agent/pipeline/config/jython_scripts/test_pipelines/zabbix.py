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


try:
    res = requests.post(
        sdc.userParams['URL'] + '/api_jsonrpc.php',
        json={
            'jsonrpc': '2.0',
            'method': 'user.login',
            'params': {'user': sdc.userParams['USER'],
                       'password': sdc.userParams['PASSWORD']},
            'id': 1,
            'auth': None,
        },
        verify=sdc.userParams['VERIFY_SSL'],
        timeout=sdc.userParams['REQUEST_TIMEOUT']
    )
    res.raise_for_status()
    if 'error' in res.json():
        raise Exception('Authentication error')
except Exception as e:
    sdc.log.error(str(e))
    sdc.log.error(traceback.format_exc())
    raise
