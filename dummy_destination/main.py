import os
import json
import time
from flask import Flask, request

OUTPUT_DIR = os.environ.get('OUTPUT_DIR', 'log')


app = Flask(__name__)
app.secret_key = b"\xf9\x19\x8d\xd2\xb7N\x84\xae\x16\x0f'`U\x88x&\nF\xa2\xe9\xa1\xd7\x8b\t"


@app.route('/api/v1/metrics', methods=['POST', 'GET'])
def to_file():
    data = request.json
    if len(data) > 0:
        with open(os.path.join(OUTPUT_DIR, data[0]['tags']['pipeline_id'][0] + '.json'), 'a+') as f:
            json.dump(request.json, f)
            f.write('\n')
    return 'ok'


if __name__ == '__main__':
    app.run()
