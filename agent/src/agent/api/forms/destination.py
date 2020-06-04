from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField
from wtforms.validators import DataRequired, URL, ValidationError


def validate_proxy(form, field):
    if form.use_proxy.data and not field.data:
        raise ValidationError(f'Field must not be empty')


class DestinationForm(FlaskForm):
    destination_url = StringField('Destination URL', [DataRequired()])
    data_collection_token = StringField('Data collection token', [DataRequired()])
    access_key = StringField('Access key')
    use_proxy = BooleanField('Use proxy')
    proxy_uri = StringField('Proxy URI', [
        # URL(False, 'Proxy url is invalid'),
        validate_proxy])
    proxy_username = StringField('Proxy username', [validate_proxy])
    proxy_password = StringField('Proxy password')
