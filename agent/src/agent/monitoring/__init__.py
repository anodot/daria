from prometheus_client import generate_latest


def get_latest():
    return generate_latest()
