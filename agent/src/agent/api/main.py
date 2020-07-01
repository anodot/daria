from flask import Flask
from agent.api.routes.destination import destination
import agent.api.routes.source as source
import wtforms_json

wtforms_json.init()

app = Flask(__name__)
app.register_blueprint(destination)
app.register_blueprint(source.source)
app.config['WTF_CSRF_ENABLED'] = False


if __name__ == "__main__":
    app.run()
