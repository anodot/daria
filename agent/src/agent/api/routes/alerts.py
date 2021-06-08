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


# todo When communication with the Anodot API is not possible.
# сделать дименшены конфигурируемыми
@alerts.route('/alert/status', methods=['GET'])
def get_alert_status():
    form = AlertStatusForm(request.args)
    if not form.validate():
        return jsonify({
            'status': 'Abnormal request',
            'errors': form.errors,
        }), 400
    try:
        alert_groups = AnodotApiClient(destination.repository.get()).get_alerts_by_status({
            'startTime': form.start_time.data,
            'status': 'OPEN',
        })
    except destination.repository.DestinationNotExists as e:
        return jsonify({
            'status': 'Not connected',
            'errors': [str(e)],
        }), 400
    except requests.exceptions.HTTPError as e:
        return jsonify(str(e)), 500

    _filter_groups_by_name(alert_groups, form.alert_name.data)
    _filter_group_alerts_by_host(alert_groups, form.host.data)
    alert_groups = alert_groups['alertGroups']
    if len(alert_groups) == 0 or len(alert_groups[0]['alerts']) == 0:
        return jsonify({'status': 'No alert'})
    return jsonify({
        'status': alert_groups[0]['alerts'][0]['status']
    })


# todo don't set startTime, take all open alerts
@alerts.route('/alerts', methods=['GET'])
def get_alerts_by_status():
    form = AlertsByStatusForm(request.args)
    if not form.validate():
        return jsonify({
            'status': 'Abnormal request',
            'errors': form.errors,
        }), 400
    try:
        alert_groups = AnodotApiClient(destination.repository.get()).get_alerts_by_status({
            'status': form.status,
            'order': form.order,
            'sort': form.sort,
            'startTime': form.start_time,
        })
    except destination.repository.DestinationNotExists as e:
        return jsonify({
            'status': 'Not connected',
            'errors': [str(e)],
        }), 400
    except requests.exceptions.HTTPError as e:
        return jsonify(str(e)), 500

    # _filter_metric_dimensions(alert_groups, 'host')
    _move_metric_dimensions(alert_groups)
    _move_metric_scores(alert_groups)
    # alert_groups['total'] = len(alert_groups['alertGroups'])
    return jsonify(_transform(alert_groups))


def _filter_groups_by_name(alert_groups: dict, alert_name: str):
    alert_groups['alertGroups'] = [group for group in alert_groups['alertGroups'] if group['name'] == alert_name]


def _filter_group_alerts_by_host(alert_groups: dict, host: str):
    for i, group in enumerate(alert_groups['alertGroups']):
        _filter_alerts_by_metric_host(group['alerts'], host)
        if len(group['alerts']) == 0:
            del alert_groups[i]


def _filter_alerts_by_metric_host(alerts: list, host: str):
    # this function changes the input alerts
    delete_alerts = []
    for i, alert in enumerate(alerts):
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
        del alerts[i]


# def _filter_metric_dimensions(alert_groups: dict, keep_dimension_name: str):
#     for group in alert_groups['alertGroups']:
#         for alert in group['alerts']:
#             for metric in alert['metrics']:
#                 to_delete = []
#                 for i, dimension in enumerate(metric['properties']):
#                     if dimension['key'] != keep_dimension_name:
#                         to_delete.append(i)
#                 to_delete.sort(reverse=True)
#                 for i in to_delete:
#                     del metric['properties'][i]


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
                    if interval['status'] == 'OPEN' and 'score' in interval:
                        metric['score'] = interval['value']
                        break


def _transform(alert_groups: dict) -> dict:
    alert_groups = _recursive_transform(
        deepcopy(alert_groups),
        deepcopy(TRANSFORM_ALERT_GROUPS)
    )
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

[
    {
        'alert_id_1': 'afhadsf',
        'status': 'open',
    },
    {
        'alert_id_2': 'different',
        'status': 'close',
    },
]
