import os
import ssl

ANODOT_API_URL = os.environ.get('ANODOT_API_URL', 'https://api.anodot.com')
ENV_PROD = True if os.environ.get('ENV_PROD') == 'true' else False

HOSTNAME = os.environ.get('HOSTNAME', 'agent')

STREAMSETS_PREVIEW_TIMEOUT = os.environ.get('STREAMSETS_PREVIEW_TIMEOUT', 30000)
STREAMSETS_MAX_RETRY_ATTEMPTS = int(os.environ.get('STREAMSETS_MAX_RETRY_ATTEMPTS', 5))

VALIDATION_ENABLED = os.environ.get('VALIDATION_ENABLED', 'true') == 'true'
DISABLE_PIPELINE_ERROR_NOTIFICATIONS = os.environ.get('DISABLE_PIPELINE_ERROR_NOTIFICATIONS', 'false') == 'true'

AGENT_DEFAULT_URL = os.environ.get('AGENT_URL', 'http://anodot-agent')

ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

AGENT_DB_HOST = os.environ.get('AGENT_DB_HOST', 'db')
AGENT_DB_USER = os.environ.get('AGENT_DB_USER', 'agent')
AGENT_DB_PASSWORD = os.environ.get('AGENT_DB_USER', 'agent')
AGENT_DB = os.environ.get('AGENT_DB', 'agent')
BACKUP_DIRECTORY = os.environ.get('BACKUP_DIRECTORY', '/usr/src/app/backup-data')

DEFAULT_STREAMSETS_URL = os.environ.get('STREAMSETS_URL', 'http://dc:18630')
DEFAULT_STREAMSETS_USERNAME = os.environ.get('STREAMSETS_USERNAME', 'admin')
DEFAULT_STREAMSETS_PASSWORD = os.environ.get('STREAMSETS_PASSWORD', 'admin')

MONITORING_URL = os.environ.get('MONITORING_URL')
MONITORING_TOKEN = os.environ.get('MONITORING_TOKEN')
MONITORING_SEND_TO_CLIENT = True if os.environ.get('MONITORING_SEND_TO_CLIENT', 'true') == 'true' else False
MONITORING_SEND_TO_ANODOT = True if os.environ.get('MONITORING_SEND_TO_ANODOT', 'true') == 'true' else False
MONITORING_COLLECT_ALL_STAGES_PROCESSING_TIME = True if os.environ.get('MONITORING_COLLECT_ALL_STAGES_PROCESSING_TIME',
                                                                       'false') == 'true' else False

_agent_listen_port = os.environ.get('LISTEN_PORT', 80)
AGENT_MONITORING_ENDPOINT = os.environ.get('AGENT_MONITORING_ENDPOINT',
                                           f'http://localhost:{_agent_listen_port}/monitoring')

SEND_TO_BC = True if os.environ.get('SEND_PIPELINE_INFO_TO_ANODOT', 'true') == 'true' else False

TLS_VERSION = ssl.PROTOCOL_TLSv1_1 if os.environ.get('TLS_VERSION', '1.2') == '1.1' else ssl.PROTOCOL_TLSv1_2
