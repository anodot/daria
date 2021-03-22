from abc import ABCMeta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from agent.modules.constants import AGENT_DB_HOST, AGENT_DB_USER, AGENT_DB_PASSWORD, AGENT_DB
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta


class DeclarativeABCMeta(DeclarativeMeta, ABCMeta):
    pass


Entity = declarative_base(metaclass=DeclarativeABCMeta)
Session = scoped_session(sessionmaker(
    bind=create_engine(f'postgresql://{AGENT_DB_USER}:{AGENT_DB_PASSWORD}@{AGENT_DB_HOST}/{AGENT_DB}')
))
