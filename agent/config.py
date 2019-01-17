streamsets_username = ''
streamsets_password = ''
streamsets_api_base_url = 'http://localhost:18630'

log_file_path = 'agent.log'

try:
    from .config_local import *
except ImportError:
    pass
