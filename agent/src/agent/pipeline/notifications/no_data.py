import re
from agent.modules.db import Entity
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
# from agent import pipeline


def get_period_in_minutes(param: str) -> int:
    print(param)
    hours = re.findall("(\d+)h", param)
    minutes = re.findall("(\d+)m", param)
    return (int(hours[0]) * 60 if hours else 0) + (int(minutes[0]) if minutes else 0)


class NoDataNotifications(Entity):
    __tablename__ = 'no_data_notifications'

    id = Column(Integer, primary_key=True)
    pipeline_id = Column(String, ForeignKey('pipelines.name'), primary_key=True)
    notification_id = Column(String, ForeignKey('pipeline_notifications.id'), primary_key=True)

    notification_period = Column(Integer)  # In minutes
    notification_sent = Column(Boolean, default=False)

    def __init__(self, pipeline_, notification_period: str):
        self.pipeline_id = pipeline_.name
        self.notification_period = get_period_in_minutes(notification_period)
        self.notification_sent = False
