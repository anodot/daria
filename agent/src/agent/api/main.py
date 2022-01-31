from flask import Flask, jsonify
from agent.api.routes.destination import destination
from agent.api.routes import source, pipeline, scripts
from agent.modules import wtforms_json
from agent.version import __version__

wtforms_json.init()

app = Flask(__name__)
app.register_blueprint(destination)
app.register_blueprint(source.sources)
app.register_blueprint(pipeline.pipelines)
app.register_blueprint(scripts.scripts)
app.config['WTF_CSRF_ENABLED'] = False


@app.route('/version', methods=['GET'])
def version():
    return jsonify('Daria Agent version: ' + __version__)


if __name__ == "__main__":
    app.run()
