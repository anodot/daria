from flask import Blueprint, request

from agent.api.forms.destination import DestinationForm
from agent.destination import HttpDestination

destination = Blueprint('destination', __name__)


@destination.route('/destination', methods=['GET'])
def get():
    return 'get'


@destination.route('/destination', methods=['POST'])
def create():
    form = DestinationForm(request.args)
    if not form.validate():
        return form.errors
    dest = HttpDestination.get()
    dest.token = form.data_collection_token.data
    if form.access_key.data:
        dest.api_key = form.access_key.data
    if form.destination_url.data:
        dest.url = form.destination_url.data
    if form.use_proxy.data:
        dest.set_proxy(True, form.proxy_uri.data, form.proxy_username.data, form.proxy_password.data)
    # todo dest.update_urls()
    dest.save()
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
