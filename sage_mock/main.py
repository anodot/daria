import os
import json
import time
from flask import Flask, request, make_response, jsonify

OUTPUT_DIR = os.environ.get('OUTPUT_DIR', 'log')

app = Flask(__name__)
app.secret_key = b"\xf9\x19\x8d\xd2\xb7N\x84\xae\x16\x0f'`U\x88x&\nF\xa2\xe9\xa1\xd7\x8b\t"


@app.route('/api/search', methods=['POST'])
def search():
    token = request.headers.get('Authorization')
    if token != 'Bearer correct_token':
        return make_response(jsonify({'status': 'fail'}), 401)
    return {'status': 'ok'}


if __name__ == '__main__':
    app.run()
