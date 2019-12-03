import os
import json
import time
from flask import Flask, request

OUTPUT_FILE = os.environ.get('OUTPUT_FILE', 'output.log')


app = Flask(__name__)
app.secret_key = b"\xf9\x19\x8d\xd2\xb7N\x84\xae\x16\x0f'`U\x88x&\nF\xa2\xe9\xa1\xd7\x8b\t"

partitions_number = 10
partitions = {}


def init_partitions():
    global partitions

    partitions = {str(i): {"last_out": 0, "last_in": 0, "offset": -1} for i in range(partitions_number)}


init_partitions()
print(partitions)


@app.route('/api/v1/metrics', methods=['POST', 'GET'])
def to_file():
    global partitions
    with open('/app/log/ooo.log', 'a+') as f:
        f.write(f"Batch start {len(request.json)} - {int(time.time_ns()/1e9)}\n")
        for i in request.json:
            timestamp = int(i['timestamp'])
            partition = i['properties']['partition']
            offset = i['properties']['offset']
            if offset == 0:
                partitions[partition]['last_in'] = 0
                partitions[partition]['last_out'] = 0
            if timestamp < partitions[partition]['last_in']:
                f.write(f"ooo inside batch: {timestamp}. last time batch {partitions[partition]['last_in']}. partition {partition}\n")
            if timestamp < partitions[partition]['last_out']:
                f.write(f"ooo outside batch: {timestamp}. last time {partitions[partition]['last_out']}. partition {partition}\n")
            partitions[partition]['last_in'] = timestamp

        f.write(f'{partition} - {offset}\n')
        for p in range(partitions_number):
            partitions[str(p)]['last_out'] = partitions[str(p)]['last_in']
            partitions[str(p)]['last_in'] = 0

    # with open(OUTPUT_FILE, 'a+') as f:
    #     json.dump(request.json, f)
    #     f.write('\n')
    return 'ok'


if __name__ == '__main__':
    app.run()
