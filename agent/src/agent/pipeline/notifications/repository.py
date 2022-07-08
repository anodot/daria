# from agent import pipeline
from agent.pipeline.notifications import PiplineNotifications, NoDataNotifications
from agent.pipeline.notifications.no_data import get_period_in_minutes
from agent.modules.db import Session


def create_notifications(pipeline_, session: Session):
    if notifies := pipeline_.config.get("notifications"):
        pipeline_.notifications = PiplineNotifications()
        if no_data_notification := notifies.get('no_data'):
            pipeline_.notifications.no_data_notification = NoDataNotifications(
                pipeline_,
                no_data_notification,
            )
            session.add(pipeline_.notifications.no_data_notification)
        session.add(pipeline_.notifications)
