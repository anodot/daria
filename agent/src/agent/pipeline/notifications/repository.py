from agent.pipeline.notifications import PiplineNotifications, NoDataNotifications
from agent.modules.db import Session


def create_notifications(pipeline_):
    if notifies := pipeline_.config.get("notifications"):
        pipeline_.notifications = PiplineNotifications()
        if no_data_notification := notifies.get('no_data'):
            pipeline_.notifications.no_data_notification = NoDataNotifications(
                pipeline_,
                no_data_notification,
                notifies.get('no_data_dvp', '24h')
            )
            Session.add(pipeline_.notifications.no_data_notification)
        Session.add(pipeline_.notifications)
