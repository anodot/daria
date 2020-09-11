import datetime
import os

from setuptools import setup, find_packages

app_version = '2.0.1'


def build_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


with open(os.path.join(os.path.dirname(__file__), 'src/agent/version.py'), 'w') as f:
    f.write(f'__version__ = "{app_version}"\n')
    f.write(f'__git_sha1__ = "{os.environ["GIT_SHA1"]}"\n')
    f.write(f'__build_time__ = "{build_time()}"\n')

setup(
    name='agent',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    entry_points='''
        [console_scripts]
        agent=agent.cli:agent
    ''',
    zip_safe=False,
    version=app_version
)
