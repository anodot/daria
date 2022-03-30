global sdc

try:
    sdc.importLock()
    import time
    import sys
    import os
    import base64
    import json
    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import requests
finally:
    sdc.importUnlock()


def is_expired(auth_token):
    res = auth_token.split('.')[1]
    res = base64.b64decode(res)
    expiration_timestamp = json.loads(res)['exp']
    return expiration_timestamp < time.time()


def get_auth_token():
    response = requests.post(
        sdc.userParams['REFRESH_TOKEN_URL'],
        json={'refreshToken': sdc.userParams['ACCESS_TOKEN']},
        proxies=sdc.userParams['PROXIES']
    )
    response.raise_for_status()
    return response.text.replace('"', '')


def main():
    for record in sdc.records:
        auth_token = None
        if 'auth_token' in sdc.state:
            auth_token = sdc.state['auth_token']
        if auth_token is None or is_expired(auth_token):
            auth_token = get_auth_token()
            sdc.state['auth_token'] = auth_token
        try:
            s = requests.Session()
            s.headers.update({
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + auth_token,
            })
            res = s.post(sdc.userParams['EVENTS_URL'], json=record.value, proxies=sdc.userParams['PROXIES'])
            res.raise_for_status()
        except Exception as e:
            message = str(e)
            if isinstance(e, requests.exceptions.HTTPError) and res.status_code == 400:
                message += ': ' + res.json()['message']
            sdc.error.write(record, message)


main()