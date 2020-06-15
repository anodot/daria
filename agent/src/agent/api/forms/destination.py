from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, URL, Optional


class DestinationForm(FlaskForm):
    data_collection_token = StringField('Data collection token', [DataRequired()])
    destination_url = StringField('Destination URL', [
        Optional(), URL(False, 'Wrong url format, please specify the protocol and domain name')
    ])
    host_id = StringField('Host ID')
    access_key = StringField('Access key')
    proxy_uri = StringField('Proxy URI', [Optional(), URL(False, 'Proxy url is invalid')])
    proxy_username = StringField('Proxy username')
    proxy_password = StringField('Proxy password')


class EditDestinationForm(DestinationForm):
    data_collection_token = StringField('Data collection token')
