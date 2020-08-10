import requests


def test_flask_app(cli_runner):
    res = requests.get('http://localhost/version')
    res.raise_for_status()
