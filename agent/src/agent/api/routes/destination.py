from agent import destination
from flask import Blueprint, request
from agent.api.forms.destination import DestinationForm, EditDestinationForm

destination_ = Blueprint('destination', __name__)


@destination_.route('/destination', methods=['GET'])
def get():
    if not destination.repository.exists():
        return 'Destination doesn\'t exist', 404
    return destination.repository.get().to_dict(), 200


@destination_.route('/destination', methods=['POST'])
def create():
    if destination.repository.exists():
        return 'Destination already exists', 400
    form = DestinationForm.from_json(request.get_json())
    if not validate():
        return form.errors, 400
    result = destination.manager.create(
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


@destination_.route('/destination', methods=['PUT'])
def edit():
    if not destination.repository.exists():
        return 'Destination doesn\'t exist', 400
    form = EditDestinationForm.from_json(request.get_json())
    if not validate():
        return form.errors, 400
    result = destination.manager.edit(
        destination.repository.get(),
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


@destination_.route('/destination', methods=['DELETE'])
def delete():
    if destination.repository.exists():
        destination.manager.delete()
    return '', 200
