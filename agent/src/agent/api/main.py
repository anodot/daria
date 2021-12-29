from flask import Flask, jsonify
from agent import di
from agent.api.routes.alerts import alerts
from agent.api.routes import data_extractors
from agent.modules import logger, db, wtforms_json
from agent.api.routes.monitoring import monitoring_bp
from agent.api.routes.streamsets import streamsets
from agent.api.routes.destination import destination_
from agent.api.routes import source, pipeline, scripts
from agent.version import __version__

logger_ = logger.get_logger(__name__)

wtforms_json.init()

app = Flask(__name__)
app.register_blueprint(streamsets)
app.register_blueprint(destination_)
app.register_blueprint(source.sources)
app.register_blueprint(pipeline.pipelines)
app.register_blueprint(scripts.scripts)
app.register_blueprint(monitoring_bp)
app.register_blueprint(data_extractors.cacti)
app.register_blueprint(data_extractors.snmp)
app.register_blueprint(data_extractors.topology)
app.register_blueprint(alerts)
app.config['WTF_CSRF_ENABLED'] = False
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False


@app.before_request
def before_request_func():
    di.init()


@app.teardown_request
def teardown_request_func(exception):
    db.Session.close()
    if exception:
        logger_.error(exception)


@app.route('/version', methods=['GET'])
def version():
    return jsonify('Daria Agent version ' + __version__)
