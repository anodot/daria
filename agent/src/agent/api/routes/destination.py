from flask import Blueprint, request
from agent.api.forms.destination import DestinationForm
from agent.destination.http import build
from agent.destination import Proxy

destination = Blueprint('destination', __name__)


@destination.route('/destination', methods=['GET'])
def get():
    return 'get'


@destination.route('/destination', methods=['POST'])
def create():
    form = DestinationForm(request.args)
    if not form.validate():
        return form.errors
    proxy = \
        Proxy(form.proxy_uri.data, form.proxy_username.data, form.proxy_password.data) if form.use_proxy.data else None
    dest = build(
        form.data_collection_token.data,
        form.destination_url.data,
        form.access_key.data,
        proxy,
        form.host_id.data,
    )
    return dest.to_dict()


@destination.route('/destination', methods=['PUT'])
def edit():
    return 'create'


@destination.route('/destination', methods=['DELETE'])
def delete():
    return 'create'


@destination.route('/nfr', methods=['GET'])
def new():
    return 'nfr'
