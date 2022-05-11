global sdc

try:
    sdc.importLock()
    import time
    import sys
    import os
    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import requests
    import anodot_api_client
finally:
    sdc.importUnlock()

REQUEST_RETRIES = 3


def main():
    for record in sdc.records:
        send_event(record)
        sdc.output.write(record)


def send_event(record):
    client = anodot_api_client.AnodotApiClient(
        sdc.state, sdc.userParams['REFRESH_TOKEN_URL'], sdc.userParams['ACCESS_TOKEN'], sdc.userParams['PROXIES']
    )
    i = 0
    while True:
        try:
            res = client.post(sdc.userParams['EVENTS_URL'], json=record.value, proxies=sdc.userParams['PROXIES'])
            res.raise_for_status()
        except (requests.ConnectionError, requests.HTTPError) as e:
            if isinstance(e, requests.exceptions.HTTPError) and 400 <= res.status_code < 500:
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