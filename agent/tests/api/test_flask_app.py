import requests


def test_flask_app():
    res = requests.get('http://localhost/version')
    res.raise_for_status()
