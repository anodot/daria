import os

SOURCES_DIR = os.path.join(os.environ.get('DATA_DIR', 'data'), 'sources')
PIPELINES_DIR = os.path.join(os.environ.get('DATA_DIR', 'data'), 'pipelines')
DESTINATION_FILE = os.path.join(os.environ.get('DATA_DIR', 'data'), 'destination.json')

SDC_DATA_PATH = os.environ.get('SDC_DATA_PATH', '/sdc-data')
SDC_RESULTS_PATH = os.path.join(SDC_DATA_PATH, 'out')
