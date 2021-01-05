from . import metrics, streamsets

from prometheus_client import generate_latest


def get_latest():
    streamsets.get_metrics()
    return generate_latest()
