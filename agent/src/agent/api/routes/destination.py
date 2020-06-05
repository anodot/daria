from typing import Optional

from flask import Blueprint, request
from agent.api.forms.destination import DestinationForm, EditDestinationForm
from agent.destination.http import create as create_destination, edit as edit_destination, HttpDestination
from agent.destination import Proxy

destination = Blueprint('destination', __name__)


def __get_proxy(form: DestinationForm) -> Optional[Proxy]:
    return \
        Proxy(form.proxy_uri.data, form.proxy_username.data, form.proxy_password.data) if form.use_proxy.data else None


@destination.route('/destination', methods=['GET'])
def get():
    if not HttpDestination.exists():
        return 'Destination doesn\'t exist', 400
    return HttpDestination.get().to_dict()


@destination.route('/destination', methods=['POST'])
def create():
    form = DestinationForm(request.args)
    if not form.validate():
        return form.errors, 400
    dest = create_destination(
        form.data_collection_token.data,
        form.destination_url.data,
        form.access_key.data,
        __get_proxy(form),
        form.host_id.data,
    )
    return dest.to_dict(), 200


@destination.route('/destination', methods=['PUT'])
def edit():
    if not HttpDestination.exists():
        return 'Destination doesn\'t exist', 400
    form = EditDestinationForm(request.args)
    if not form.validate():
        return form.errors
    dest = edit_destination(
        form.data_collection_token.data,
        form.destination_url.data,
        form.access_key.data,
        __get_proxy(form),
        form.host_id.data,
    )
    return dest.to_dict(), 200
