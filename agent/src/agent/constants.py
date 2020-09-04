import os

SDC_DATA_PATH = os.environ.get('SDC_DATA_PATH', '/sdc-data')
SDC_RESULTS_PATH = os.path.join(SDC_DATA_PATH, 'out')

ERRORS_DIR = os.path.join(SDC_DATA_PATH, 'errors')

ANODOT_API_URL = os.environ.get('ANODOT_API_URL', 'https://api.anodot.com')
ENV_PROD = True if os.environ.get('ENV_PROD') == 'true' else False

HOSTNAME = os.environ.get('HOSTNAME', 'agent')

STREAMSETS_PREVIEW_TIMEOUT = os.environ.get('STREAMSETS_PREVIEW_TIMEOUT', 30000)

MONITORING_SOURCE_NAME = 'monitoring'

VALIDATION_ENABLED = True if os.environ.get('VALIDATION_ENABLED') == 'true' else False

AGENT_URL = os.environ.get('AGENT_URL', 'http://anodot-agent')

# todo this constant is wrong
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

AGENT_DB_HOST = os.environ.get('AGENT_DB_HOST', 'localhost')
AGENT_DB_USER = os.environ.get('AGENT_DB_USER', 'agent')
AGENT_DB_PASSWORD = os.environ.get('AGENT_DB_USER', 'agent')
