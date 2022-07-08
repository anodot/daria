import re
from agent.modules.db import Entity
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TIMESTAMP
# from agent import pipeline


def get_period_in_minutes(param: str) -> int:
    print(param)
    hours = re.findall("(\d+)h", param)
    minutes = re.findall("(\d+)m", param)
    return (int(hours[0]) * 60 if hours else 0) + (int(minutes[0]) if minutes else 0)


class NoDataNotifications(Entity):
    __tablename__ = 'no_data_notifications'

    id: int = Column(Integer, primary_key=True)
    pipeline_id: str = Column(String, ForeignKey('pipelines.name'), primary_key=True)
    notification_id: str = Column(Integer, ForeignKey('pipeline_notifications.id'), primary_key=True)

    notification_period: int = Column(Integer, nullable=False)  # In minutes
    notification_sent: bool = Column(Boolean, default=False)

    last_updated = Column(TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now())

    def __init__(self, pipeline_, notification_period: str):
        self.pipeline_id = pipeline_.name
        self.notification_period = get_period_in_minutes(notification_period)
        self.notification_sent = False
