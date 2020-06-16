from flask import Flask

app = Flask(__name__)


@app.route('/sources', methods=['GET'])
def list_sources():
    return 'Create source'


@app.route('/sources', methods=['POST'])
def create():
    return 'Create a source'


@app.route('/source/<source_id>', methods=['PUT'])
def edit(source_id):
    return 'Edit source'


@app.route('/source/<source_id>', methods=['DELETE'])
def delete(source_id):
    return 'Delete source'
