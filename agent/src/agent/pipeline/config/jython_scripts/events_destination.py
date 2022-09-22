global sdc

try:
    sdc.importLock()
    import time
    import sys
    import os
    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import requests
    from anodot_api_client import AnodotApiClient
finally:
    sdc.importUnlock()

REQUEST_RETRIES = 3


def main():
    for record in sdc.records:
        send_event(record)
        sdc.output.write(record)


def send_offset(offset):
    try:
        res = requests.post(sdc.userParams['AGENT_OFFSET_URL'], json={'offset': offset})
        res.raise_for_status()
    except (requests.ConnectionError, requests.HTTPError) as e:
        sdc.error.write(str(e))


def send_event(record):
    client = AnodotApiClient(
        sdc.state, sdc.userParams['ANODOT_URL'], sdc.userParams['ACCESS_TOKEN'], sdc.userParams['PROXIES']
    )
    i = 0
    while True:
        i += 1
        try:
            res = client.send_events({'event': record.value['event']})
            res.raise_for_status()
            send_offset(record.value['offset'])
        except (requests.ConnectionError, requests.HTTPError) as e:
            if isinstance(e, requests.exceptions.HTTPError) and 400 <= res.status_code < 500:
                message = str(e)
                if 'message' in res.json():
                    message += ': ' + res.json()['message']
                sdc.error.write(record, message)
                break
            elif i < REQUEST_RETRIES:
                time.sleep(10)
                continue
            sdc.error.write(record, str(e))
            break
        break


main()