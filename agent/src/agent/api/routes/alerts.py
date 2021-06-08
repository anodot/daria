import requests

from copy import deepcopy
from flask import Blueprint, request, jsonify
from agent import destination
from agent.api.forms.alerts import AlertsByStatusForm, AlertStatusForm
from agent.destination.anodot_api_client import AnodotApiClient

alerts = Blueprint('alerts', __name__)

TRANSFORM_ALERT_GROUPS = {
    'keep': ['total', 'alertGroups'],
    'alertGroups': {
        'keep': ['id', 'name', 'alerts'],
        'alerts': {
            'keep': ['status', 'startTime', 'updateTime', 'endTime', 'metrics'],
            'metrics': {
                'keep': ['what', 'host', 'score'],
            }
        }
    }
}
OPEN = 'OPEN'
CLOSE = 'CLOSE'


@alerts.route('/alert/status', methods=['GET'])
def get_alert_status():
    form = AlertStatusForm(request.args)
    if not form.validate():
        return jsonify({
            'status': 'Abnormal request',
            'errors': form.errors,
        }), 400
    try:
        alert_groups = AnodotApiClient(destination.repository.get()).get_alerts({
            'startTime': form.start_time.data,
        })
    except destination.repository.DestinationNotExists as e:
        return jsonify({
            'status': 'Not connected',
            'errors': {'destination': [str(e)]},
        }), 400
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return jsonify({
                'status': 'Not connected',
                'errors': {'Unauthorized': [str(e)]},
            }), 401
        return jsonify({
                'status': 'Not connected',
                'errors': {'HTTPError': [str(e)]},
            }), 500

    _filter_groups_by_name(alert_groups, form.alert_name.data)
    _filter_group_alerts_by_host(alert_groups, form.host.data)

    alert_groups = alert_groups['alertGroups']
    if len(alert_groups) == 0 or len(alert_groups[0]['alerts']) == 0:
        return jsonify({'status': 'No alert'})
    return jsonify(_extract_alert_statuses(alert_groups))


@alerts.route('/alerts', methods=['GET'])
def get_alerts():
    form = AlertsByStatusForm(request.args)
    if not form.validate():
        return jsonify({
            'status': 'Abnormal request',
            'errors': form.errors,
        }), 400
    try:
        params = {
            'status': form.status.data,
            'order': form.order.data,
            'sort': form.sort.data,
        }
        # apply time constraints only to CLOSE status
        if form.status.data != OPEN:
            params['startTime'] = form.start_time.data
        alert_groups = AnodotApiClient(destination.repository.get()).get_alerts(params)
    except destination.repository.DestinationNotExists as e:
        return jsonify({
            'status': 'Not connected',
            'errors': {'destination': [str(e)]},
        }), 400
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return jsonify({
                'status': 'Not connected',
                'errors': {'Unauthorized': [str(e)]},
            }), 400
        return jsonify({
            'status': 'Not connected',
            'errors': {'HTTPError': [str(e)]},
        }), 500

    _move_metric_dimensions(alert_groups)
    _move_metric_scores(alert_groups)
    return jsonify(_transform(alert_groups))


def _filter_groups_by_name(alert_groups: dict, alert_name: str):
    alert_groups['alertGroups'] = [group for group in alert_groups['alertGroups'] if group['name'] == alert_name]
    _set_total(alert_groups)


def _filter_group_alerts_by_host(alert_groups: dict, host: str):
    to_delete = []
    for i, group in enumerate(alert_groups['alertGroups']):
        _filter_alerts_by_metric_host(group['alerts'], host)
        if len(group['alerts']) == 0:
            to_delete.append(i)
    for i in to_delete:
        del alert_groups['alertGroups'][i]


def _filter_alerts_by_metric_host(alerts_: list, host: str):
    delete_alerts = []
    for i, alert in enumerate(alerts_):
        correct_host = False
        # if at least one metric in the alert has the correct host - we keep this alert
        for metric in alert['metrics']:
            for dimension in metric['properties']:
                if dimension['key'] == 'host' and dimension['value'] == host:
                    correct_host = True
                    break
            if correct_host:
                break
        if not correct_host:
            delete_alerts.append(i)
    for i in delete_alerts:
        del alerts_[i]


def _extract_alert_statuses(alert_groups: list) -> list:
    statuses = []
    for group in alert_groups:
        for alert in group['alerts']:
            statuses.append({
                'id': alert['id'],
                'status': alert['status'],
            })
    return statuses


def _move_metric_dimensions(alert_groups: dict):
    for group in alert_groups['alertGroups']:
        for alert in group['alerts']:
            for metric in alert['metrics']:
                for dimension in metric['properties']:
                    metric[dimension['key']] = dimension['value']
                del metric['properties']


def _move_metric_scores(alert_groups: dict):
    for group in alert_groups['alertGroups']:
        for alert in group['alerts']:
            for metric in alert['metrics']:
                for interval in metric['intervals']:
                    if interval['status'] == OPEN and 'score' in interval:
                        metric['score'] = interval['value']
                        break


def _transform(alert_groups: dict) -> dict:
    alert_groups = _recursive_transform(
        deepcopy(alert_groups),
        deepcopy(TRANSFORM_ALERT_GROUPS)
    )
    _set_total(alert_groups)
    return alert_groups


def _recursive_transform(dict_: dict, transform_config: dict) -> dict:
    keep = transform_config.pop('keep')
    for k in list(dict_.keys()):
        if k not in keep:
            del dict_[k]

    for k, v in dict_.items():
        if k in transform_config:
            for v2 in v:
                _recursive_transform(v2, deepcopy(transform_config[k]))

    return dict_


def _set_total(alert_groups):
    # sometimes the total value is incorrect, so we calculate in on our own
    alert_groups['total'] = len(alert_groups['alertGroups'])
