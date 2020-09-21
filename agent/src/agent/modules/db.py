from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from agent.modules.constants import AGENT_DB_HOST, AGENT_DB_USER, AGENT_DB_PASSWORD
from sqlalchemy.ext.declarative import declarative_base

Entity = declarative_base()
Session = sessionmaker(
    bind=create_engine(f'postgresql://{AGENT_DB_USER}:{AGENT_DB_PASSWORD}@{AGENT_DB_HOST}/agent')
)
_session = None


def session():
    global _session
    if not _session:
        _session = Session()
    return _session


def close_session():
    global _session
    if _session:
        _session.close()
        _session = None
