import wtforms_json

from flask import Flask
from agent.api.routes.destination import destination
from agent.api.routes import source, pipeline

wtforms_json.init()

app = Flask(__name__)
app.register_blueprint(destination)
app.register_blueprint(source.sources)
app.register_blueprint(pipeline.pipelines)
app.config['WTF_CSRF_ENABLED'] = False


if __name__ == "__main__":
    app.run()
