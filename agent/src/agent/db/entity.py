from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, JSON, ForeignKey

Base = declarative_base()


class Source(Base):
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    config = Column(JSON)

    pipelines = relationship("Pipeline")


class Pipeline(Base):
    __tablename__ = 'pipelines'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    source_id = Column(Integer, ForeignKey('sources.id'))
    config = Column(JSON)
