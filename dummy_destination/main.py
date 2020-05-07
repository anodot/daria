import os
import json
import time
import uuid
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


@app.route('/api/v1/metrics/watermark', methods=['POST'])
def watermark_mock():
    data = request.json
    with open(os.path.join(OUTPUT_DIR, data['schemaId'] + '_watermark.json'), 'w') as f:
        json.dump(data, f)
    return json.dumps({'errors': []})


@app.route('/api/v2/access-token', methods=['POST'])
def access_token_mock():
    return '"dfsfegfgf"'


@app.route('/api/v2/stream-schemas', methods=['POST'])
def create_schema_mock():
    response = {
        'schema': request.json,
        'meta': {
            "createdTime": time.time(),
            "modifiedTime": time.time()
        }
    }
    response['schema']['id'] = "111111-22222-3333-4444"
    return json.dumps(response)


@app.route('/api/v2/stream-schemas', methods=['DELETE'])
def delete_schema_mock():
    return 'ok'


if __name__ == '__main__':
    app.run()
