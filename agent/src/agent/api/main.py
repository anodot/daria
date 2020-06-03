from flask import Flask
from agent.api.routes.destination import destination

app = Flask(__name__)
app.register_blueprint(destination)


@app.route('/', methods=['GET'])
def hello():
    return 'Hello world!'


if __name__ == "__main__":
    app.run()
