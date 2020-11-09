import traceback
import wtforms_json

from flask import Flask, jsonify

from agent.modules import db
from agent.api.routes.streamsets import streamsets
from agent.api.routes.destination import destination_
from agent.api.routes import source, pipeline, scripts
from agent.modules.logger import get_logger
from agent.version import __version__

logger = get_logger(__name__)

wtforms_json.init()

app = Flask(__name__)
app.register_blueprint(streamsets)
app.register_blueprint(destination_)
app.register_blueprint(source.sources)
app.register_blueprint(pipeline.pipelines)
app.register_blueprint(scripts.scripts)
app.config['WTF_CSRF_ENABLED'] = False
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False


@app.teardown_request
def teardown_request_func(exception):
    try:
        if exception:
            db.session().rollback()
        else:
            db.session().commit()
        db.close_session()
    except Exception:
        logger.error(traceback.format_exc())


@app.route('/version', methods=['GET'])
def version():
    return jsonify('Daria Agent version: ' + __version__)
