import os
import json
import time

from flask import Flask, request, jsonify

OUTPUT_DIR = os.environ.get('OUTPUT_DIR', 'log')
ROLLUP_ID = '123456789'
AUTH_TOKEN = 'first_part.eyJkYXRhIjoic29tZWRhdGEiLCJpYXQiOjE2NTM5MDQ2MjIsImV4cCI6MjI1MzkwNzg2MX0.third_part'

app = Flask(__name__)
app.secret_key = b"\xf9\x19\x8d\xd2\xb7N\x84\xae\x16\x0f'`U\x88x&\nF\xa2\xe9\xa1\xd7\x8b\t"


@app.route('/api/v1/metrics', methods=['POST'])
def to_file():
    if request.args.get('token') and request.args.get('token') == 'incorrect_token':
        return json.dumps({'errors': ['Data collection token is invalid']}), 401
    data = request.json
    if data and len(data) > 0:
        _write_to_file(_extract_file_name(request.json), data)
    return json.dumps({'errors': []})


@app.route('/api/v2/user-events', methods=['POST'])
def event_to_file():
    if request.headers.get('Authorization') != f'Bearer {AUTH_TOKEN}':
        return json.dumps({'errors': ['Data collection token is invalid']}), 401
    _write_to_file(_extract_events_file_name(request.json), request.json)
    return json.dumps({'errors': []})


def _write_to_file(file_name: str, data):
    file_path = os.path.join(OUTPUT_DIR, file_name)
    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            if existing_data := json.load(f):
                data = existing_data + data
    with open(file_path, 'w') as f:
        json.dump(data, f)


def _extract_file_name(data: list[dict]):
    try:
        file_name = data[0]['tags']['pipeline_id'][0] + '_' + data[0]['tags']['pipeline_type'][0]
    except KeyError:
        file_name = data[0]['properties']['what']
    return f'{file_name}.json'


def _extract_events_file_name(data: dict):
    for prop in data['event']['properties']:
        if prop['key'] == 'pipeline_id':
            return f'{prop["value"]}.json'
    raise Exception('pipeline_id not found in event properties')


@app.route('/api/v1/alert', methods=['POST'])
def to_file_simple():
    file_name = "alert"
    with open(os.path.join(OUTPUT_DIR, f'{file_name}.json'), 'a+') as f:
        json.dump(request.json, f)
        f.write('\n')
    return ''


@app.route('/api/v1/agents', methods=['POST'])
def monitoring_api_mock():
    return json.dumps({'errors': []})


@app.route('/api/v1/metrics/watermark', methods=['POST'])
def watermark_mock():
    if request.args.get('token') and request.args.get('token') != 'correct_token':
        return json.dumps({'errors': ['Data collection token is invalid']}), 401
    data = request.json
    with open(os.path.join(OUTPUT_DIR, data['schemaId'] + '_watermark.json'), 'w') as f:
        json.dump(data, f)
    return json.dumps({'errors': []})


@app.route('/api/v1/stream-schemas/internal/', methods=['POST'])
def update_schema_mock():
    if request.args.get('token') and request.args.get('token') != 'correct_token':
        return json.dumps({'errors': ['Data collection token is invalid']}), 401

    schema = request.json
    response = {
        'schema': schema,
        'meta': {
            "createdTime": time.time(),
            "modifiedTime": time.time(),
        }
    }
    if not request.args.get('id') or request.args.get('id') != schema['id']:
        response['schema']['id'] = f'{schema["name"]}-4321'
    return json.dumps(response)


@app.route('/api/v2/access-token', methods=['POST'])
def access_token_mock():
    if request.json['refreshToken'] == 'incorrect_key':
        return 'Incorrect key', 401
    return AUTH_TOKEN, 200


@app.route('/api/v2/stream-schemas', methods=['POST'])
def create_schema_mock():
    schema = request.json
    response = {
        'schema': schema,
        'meta': {
            "createdTime": time.time(),
            "modifiedTime": time.time(),
        }
    }
    response['schema']['id'] = f'{schema["name"]}-1234'
    return json.dumps(response)


@app.route('/api/v2/stream-schemas/schemas/<schema_id>', methods=['DELETE'])
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


@app.route('/api/v2/bc/agents', methods=['DELETE'])
def delete_bc_pipeline():
    return json.dumps('ok')


@app.route('/SolarWinds/InformationService/v3/Json/Query', methods=['GET'])
def solarwinds_data_example():
    if request.headers.get('Authorization') != "Basic QWRtaW46YWRtaW4=":
        return json.dumps({'error': 'Wrong user or pass'}), 401
    predefined_query = 'SELECT TOP 1000 NodeID, DateTime, Archive, MinLoad, MaxLoad, AvgLoad, TotalMemory,' \
                       ' MinMemoryUsed, MaxMemoryUsed, AvgMemoryUsed, AvgPercentMemoryUsed FROM Orion.CPULoad' \
                       ' WHERE DateTime > DateTime(\'2021-03-30T00:00:00\')' \
                       ' AND DateTime <= AddSecond(86400, DateTime(\'2021-03-30T00:00:00\')) ORDER BY DateTime'
    if "query" in request.args and request.args["query"] == predefined_query:
        with open('data/solarwinds_data_example.json') as f:
            return json.load(f)
    # request is not correct
    return json.dumps({'results': []})


@app.route('/api/v0/devices', methods=['GET'])
def observium_devices():
    # basic auth admin:admin
    if request.headers.get('Authorization') != 'Basic YWRtaW46YWRtaW4=':
        return json.dumps({'error': 'Wrong user or pass'}), 401
    with open('data/observium_devices.json') as f:
        return json.load(f)


@app.route('/api/v0/ports', methods=['GET'])
def observium_ports():
    # basic auth admin:admin
    if request.headers.get('Authorization') != 'Basic YWRtaW46YWRtaW4=':
        return json.dumps({'error': 'Wrong user or pass'}), 401
    with open('data/observium_ports.json') as f:
        return json.load(f)


@app.route('/api/v0/mempools', methods=['GET'])
def observium_mempools():
    # basic auth admin:admin
    if request.headers.get('Authorization') != 'Basic YWRtaW46YWRtaW4=':
        return json.dumps({'error': 'Wrong user or pass'}), 401
    with open('data/observium_mempools.json') as f:
        return json.load(f)


@app.route('/api/v0/processors', methods=['GET'])
def observium_processors():
    # basic auth admin:admin
    if request.headers.get('Authorization') != 'Basic YWRtaW46YWRtaW4=':
        return json.dumps({'error': 'Wrong user or pass'}), 401
    with open('data/observium_processors.json') as f:
        return json.load(f)


@app.route('/api/v0/storage', methods=['GET'])
def observium_storage():
    # basic auth admin:admin
    if request.headers.get('Authorization') != 'Basic YWRtaW46YWRtaW4=':
        return json.dumps({'error': 'Wrong user or pass'}), 401
    with open('data/observium_storage.json') as f:
        return json.load(f)


@app.route('/api/v1/site', methods=['GET'])
def topology_site_entity():
    # basic auth admin:admin
    if request.headers.get('Authorization') != 'Basic YWRtaW46YWRtaW4=':
        return json.dumps({'error': 'Wrong user or pass'}), 401
    with open('data/site_entity.json') as f:
        return jsonify(json.load(f))


@app.route('/api/v2/topology/map/load/start', methods=['POST'])
def topology_load_start():
    if request.headers.get('Authorization') != f'Bearer {AUTH_TOKEN}':
        return json.dumps({'errors': ['Data collection token is invalid']}), 401
    return {'rollupId': ROLLUP_ID}


@app.route('/api/v2/topology/map/load/<rollup_id>', methods=['PUT'])
def topology_load_data(rollup_id):
    if rollup_id != ROLLUP_ID:
        return {'errors': ['Wrong rollup id']}, 500
    if request.headers.get('Authorization') != f'Bearer {AUTH_TOKEN}':
        return json.dumps({'errors': ['Data collection token is invalid']}), 401
    if data := [request.json]:
        for obj in data:
            _write_to_file(f'topology_{obj["type"]}.json', data)
    return {}


@app.route('/api/v2/topology/map/load/<rollup_id>/end', methods=['POST'])
def topology_load_end(rollup_id):
    if rollup_id != ROLLUP_ID:
        return {'errors': ['Wrong rollup id']}, 500
    if request.headers.get('Authorization') != f'Bearer {AUTH_TOKEN}':
        return json.dumps({'errors': ['Data collection token is invalid']}), 401
    return {}


if __name__ == '__main__':
    app.run()
