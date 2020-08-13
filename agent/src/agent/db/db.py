import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def _get_db_host():
    if os.environ.get('IS_DOCKER_ENV'):
        return 'db'
    return 'localhost:5432'


Session = sessionmaker(bind=create_engine(f'postgresql://agent:agent@{_get_db_host()}/agent'))
