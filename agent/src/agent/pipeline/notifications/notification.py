from agent.modules.db import Entity
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from agent.pipeline.notifications.no_data import NoDataNotifications


class PiplineNotifications(Entity):
    __tablename__ = 'pipeline_notifications'

    id: int = Column(Integer, primary_key=True)
    pipeline_id: str = Column(String, ForeignKey('pipelines.name'))

    no_data_notification: Mapped[NoDataNotifications] = relationship(NoDataNotifications, cascade="delete",
                                                                     uselist=False)
