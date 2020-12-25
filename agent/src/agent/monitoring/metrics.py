from prometheus_client import Info
from agent import version


VERSION = Info('version', 'Agent version')
VERSION.info({'version': version.__version__, 'build_time': version.__build_time__, 'git_sha1': version.__git_sha1__})
