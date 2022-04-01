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

REQUEST_RETRIES = 3


def is_expired(auth_token):
    res = auth_token.split('.')[1]
    res = base64.b64decode(res)
    expiration_timestamp = json.loads(res)['exp']
    # refresh token in advance just in case
    return expiration_timestamp < time.time() - 300


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
        send_event(auth_token, record)
        sdc.output.write(record)


def send_event(auth_token, record):
    i = 0
    while True:
        s = requests.Session()
        s.headers.update({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + auth_token,
        })
        try:
            res = s.post(sdc.userParams['EVENTS_URL'], json=record.value, proxies=sdc.userParams['PROXIES'], timeout=30)
            res.raise_for_status()
        except (requests.ConnectionError, requests.HTTPError) as e:
            if isinstance(e, requests.exceptions.HTTPError) and res.status_code == 400:
                message = str(e)
                if 'message' in res.json():
                    message += ': ' + res.json()['message']
                sdc.error.write(record, message)
                break
            elif i < REQUEST_RETRIES - 1:
                time.sleep(10)
                continue
            sdc.error.write(record, str(e))
            break


main()