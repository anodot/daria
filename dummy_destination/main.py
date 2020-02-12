import os
import json
import time
from flask import Flask, request

OUTPUT_DIR = os.environ.get('OUTPUT_DIR', 'log')


app = Flask(__name__)
app.secret_key = b"\xf9\x19\x8d\xd2\xb7N\x84\xae\x16\x0f'`U\x88x&\nF\xa2\xe9\xa1\xd7\x8b\t"


@app.route('/api/v1/metrics', methods=['POST'])
def to_file():
    data = request.json
    if data and len(data) > 0:
        file_name = data[0]['tags']['pipeline_id'][0] + '_' + data[0]['tags']['pipeline_type'][0]
        with open(os.path.join(OUTPUT_DIR, file_name + '.json'), 'a+') as f:
            json.dump(request.json, f)
            f.write('\n')
    return json.dumps({'errors': []})


@app.route('/api/v1/agents', methods=['POST'])
def monitoring_api_mock():
    return json.dumps({'errors': []})


if __name__ == '__main__':
    app.run()
