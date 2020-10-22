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
        try:
            file_name = data[0]['tags']['pipeline_id'][0] + '_' + data[0]['tags']['pipeline_type'][0]
        except KeyError:
            file_name = data[0]['properties']['what']
        with open(os.path.join(OUTPUT_DIR, file_name + '.json'), 'a+') as f:
            json.dump(request.json, f)
            f.write('\n')
    if request.args.get('token'):
        if request.args.get('token') == 'incorrect_token':
            return json.dumps({'errors': ['Data collection token is invalid']}), 401
    return json.dumps({'errors': []})


@app.route('/api/v1/alert', methods=['POST'])
def to_file_simple():
    file_name = "alert"
    with open(os.path.join(OUTPUT_DIR, file_name + '.json'), 'a+') as f:
        json.dump(request.json, f)
        f.write('\n')
    return ''


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
    if request.json['refreshToken'] == 'incorrect_key':
        return 'Incorrect key', 401
    return 'ok', 200


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


@app.route('/api/v2/stream-schemas/<schema_id>', methods=['DELETE'])
def delete_schema_mock(schema_id):
    return json.dumps({'result': 'ok'})


@app.route('/api/v1/status', methods=['GET'])
def status():
    return json.dumps({'result': 'ok'})


@app.route('/api/v2/topology/data', methods=['POST'])
def topology_data():
    if 'type' not in request.args:
        return 'Specify "type"', 400

    with open(os.path.join(OUTPUT_DIR, f'topology_{request.args["type"]}.gz'), 'wb') as f:
        f.write(request.get_data())
    return json.dumps({'result': 'ok'})


@app.route('/api/v2/bc/agents', methods=['POST'])
def bc_pipelines():
    return json.dumps('ok')


if __name__ == '__main__':
    app.run()
