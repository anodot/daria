import requests


def test_flask_app():
    res = requests.get('http://localhost/version')
    res.raise_for_status()


def test_di():
    res = requests.get('http://localhost/test-di')
    res.raise_for_status()
