import os

DATA_DIR = os.environ.get('DATA_DIR', 'data')
PIPELINES_DIR = os.path.join(DATA_DIR, 'pipelines')

SDC_DATA_PATH = os.environ.get('SDC_DATA_PATH', '/sdc-data')
SDC_RESULTS_PATH = os.path.join(SDC_DATA_PATH, 'out')

ERRORS_DIR = os.path.join(SDC_DATA_PATH, 'errors')

ANODOT_API_URL = os.environ.get('ANODOT_API_URL', 'https://api.anodot.com')
