from datetime import datetime, timedelta
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import AnyOf, DataRequired, Optional


class AlertStatusForm(FlaskForm):
    alert_name = StringField('Alert name', [DataRequired()])
    host = StringField('Host', [DataRequired()])
    start_time = IntegerField(
        'Start time',
        [Optional()],
        default=int((datetime.now() - timedelta(days=10)).timestamp())
    )


class AlertsByStatusForm(FlaskForm):
    status = StringField('Alert status', [DataRequired(), AnyOf(['OPEN', 'CLOSE'])])
    order = StringField('Order', [Optional(), AnyOf(['asc', 'desc'])], default='desc')
    sort = StringField(
        'Sort',
        [Optional(), AnyOf(['startTime', 'updateTime', 'duration', 'score', 'metrics'])],
        default='updateTime'
    )
    start_time = IntegerField(
        'Start time',
        [Optional()],
        default=int((datetime.now() - timedelta(days=10)).timestamp())
    )
