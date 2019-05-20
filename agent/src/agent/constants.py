import os

DATA_DIR = os.environ.get('DATA_DIR', 'data')
SOURCES_DIR = os.path.join(DATA_DIR, 'sources')
PIPELINES_DIR = os.path.join(DATA_DIR, 'pipelines')

SDC_DATA_PATH = os.environ.get('SDC_DATA_PATH', '/sdc-data')
SDC_RESULTS_PATH = os.path.join(SDC_DATA_PATH, 'out')

TIMESTAMPS_DIR = os.path.join(SDC_DATA_PATH, 'timestamps')

ANODOT_API_URL = os.environ.get('ANODOT_API_URL', 'https://api.anodot.com')
