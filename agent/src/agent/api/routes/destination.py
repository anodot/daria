import agent.destination

from flask import Blueprint, request
from agent.api.forms.destination import DestinationForm, EditDestinationForm

destination = Blueprint('destination', __name__)


@destination.route('/destination', methods=['GET'])
def get():
    if not agent.destination.HttpDestination.exists():
        return 'Destination doesn\'t exist', 404
    return agent.destination.HttpDestination.get().to_dict(), 200


@destination.route('/destination', methods=['POST'])
def create():
    form = DestinationForm.from_json(request.get_json())
    if not form.validate():
        return form.errors, 400
    result = agent.destination.create(
        form.data_collection_token.data,
        form.destination_url.data,
        form.access_key.data,
        form.proxy_uri.data,
        form.proxy_username.data,
        form.proxy_password.data,
        form.host_id.data,
    )
    if result.is_err():
        return result.value, 400
    return result.value.to_dict(), 200


@destination.route('/destination', methods=['PUT'])
def edit():
    if not agent.destination.HttpDestination.exists():
        return 'Destination doesn\'t exist', 400
    form = EditDestinationForm.from_json(request.get_json())
    if not form.validate():
        return form.errors, 400
    result = agent.destination.edit(
        agent.destination.HttpDestination.get(),
        form.data_collection_token.data,
        form.destination_url.data,
        form.access_key.data,
        form.proxy_uri.data,
        form.proxy_username.data,
        form.proxy_password,
        form.host_id.data,
    )
    if result.is_err():
        return result.value, 400
    return result.value.to_dict(), 200


@destination.route('/destination', methods=['DELETE'])
def delete():
    if agent.destination.HttpDestination.exists():
        agent.destination.HttpDestination.get().delete()
    return 'success', 200
