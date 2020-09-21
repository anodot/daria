import wtforms_json

from flask import Flask, jsonify
from agent.modules import db
from agent.api.routes.destination import destination_
from agent.api.routes import source, pipeline, scripts
from agent.version import __version__

wtforms_json.init()

app = Flask(__name__)
app.register_blueprint(destination_)
app.register_blueprint(source.sources)
app.register_blueprint(pipeline.pipelines)
app.register_blueprint(scripts.scripts)
app.config['WTF_CSRF_ENABLED'] = False


@app.before_request
def before_request_func():
    db.create_session()


@app.after_request
def after_request_func(response):
    db.close_session()
    return response


@app.route('/version', methods=['GET'])
def version():
    return jsonify('Daria Agent version: ' + __version__)
