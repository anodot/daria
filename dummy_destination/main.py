import os
import json
import time
from flask import Flask, request

OUTPUT_FILE = os.environ.get('OUTPUT_FILE', 'output.log')


app = Flask(__name__)
app.secret_key = b"\xf9\x19\x8d\xd2\xb7N\x84\xae\x16\x0f'`U\x88x&\nF\xa2\xe9\xa1\xd7\x8b\t"

# last_timestamp = 0


@app.route('/api/v1/metrics', methods=['POST', 'GET'])
def to_file():
    # global last_timestamp
    # with open('/app/log/ooo.log', 'a+') as f:
    #     f.write(f"Batch start {len(request.json)} - {int(time.time_ns()/1e9)}\n")
    #     batch_last_time = 0
    #     for i in request.json:
    #         timestamp = int(i['timestamp'])
    #         if timestamp < batch_last_time:
    #             f.write(f"ooo inside batch: {timestamp}. last time batch {batch_last_time}\n")
    #         if timestamp < last_timestamp:
    #             f.write(f"ooo outside batch: {timestamp}. last time {last_timestamp}\n")
    #         batch_last_time = timestamp
    #     last_timestamp = batch_last_time

    with open(OUTPUT_FILE, 'a+') as f:
        json.dump(request.json, f)
        f.write('\n')
    return 'ok'


if __name__ == '__main__':
    app.run()
