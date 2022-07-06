from agent.modules.db import Entity
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from agent.pipeline.notifications.no_data import NoDataNotifications


class PiplineNotifications(Entity):
    __tablename__ = 'pipeline_notifications'

    id = Column(Integer, primary_key=True)
    pipeline_id = Column(String, ForeignKey('pipelines.name'))

    no_data_notification = relationship(NoDataNotifications, cascade="delete", uselist=False)
