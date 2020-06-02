from flask import Flask

app = Flask(__name__)


@app.route('/destination', methods=['POST'])
def create():
    return 'Create destination'


@app.route('/destination', methods=['PUT'])
def edit():
    return 'Edit destination'


@app.route('/destination', methods=['DELETE'])
def delete():
    return 'Delete destination'
