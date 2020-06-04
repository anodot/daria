from flask import Flask
from agent.api.routes.destination import destination

app = Flask(__name__)
app.register_blueprint(destination)
app.config['WTF_CSRF_ENABLED'] = False


if __name__ == "__main__":
    app.run()
