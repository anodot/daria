from flask import Flask
from agent.api.routes.destination import destination
import wtforms_json

wtforms_json.init()

app = Flask(__name__)
app.register_blueprint(destination)
app.config['WTF_CSRF_ENABLED'] = False


if __name__ == "__main__":
    app.run()
