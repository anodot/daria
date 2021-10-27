import os
import json
import time
from flask import Flask, request

OUTPUT_DIR = os.environ.get('OUTPUT_DIR', 'log')

app = Flask(__name__)
app.secret_key = b"\xf9\x19\x8d\xd2\xb7N\x84\xae\x16\x0f'`U\x88x&\nF\xa2\xe9\xa1\xd7\x8b\t"


@app.route('/api/v1/metrics', methods=['POST'])
def to_file():
    if request.args.get('token'):
        if request.args.get('token') == 'incorrect_token':
            return json.dumps({'errors': ['Data collection token is invalid']}), 401
    data = request.json
    if data and len(data) > 0:
        file_path = os.path.join(OUTPUT_DIR, _extract_file_name(data) + '.json')
        if os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                existing_data = json.load(f)
                if existing_data:
                    data = existing_data + data
        with open(file_path, 'w') as f:
            json.dump(data, f)
    return json.dumps({'errors': []})


def _extract_file_name(data):
    try:
        file_name = data[0]['tags']['pipeline_id'][0] + '_' + data[0]['tags']['pipeline_type'][0]
    except KeyError:
        file_name = data[0]['properties']['what']
    return file_name


@app.route('/api/v1/alert', methods=['POST'])
def to_file_simple():
    file_name = "alert"
    with open(os.path.join(OUTPUT_DIR, file_name + '.json'), 'a+') as f:
        json.dump(request.json, f)
        f.write('\n')
    return ''


@app.route('/api/v1/agents', methods=['POST'])
def monitoring_api_mock():
    return json.dumps({'errors': []})


@app.route('/api/v1/metrics/watermark', methods=['POST'])
def watermark_mock():
    if request.args.get('token'):
        if request.args.get('token') != 'correct_token':
            return json.dumps({'errors': ['Data collection token is invalid']}), 401
    data = request.json
    with open(os.path.join(OUTPUT_DIR, data['schemaId'] + '_watermark.json'), 'w') as f:
        json.dump(data, f)
    return json.dumps({'errors': []})


@app.route('/api/v2/access-token', methods=['POST'])
def access_token_mock():
    if request.json['refreshToken'] == 'incorrect_key':
        return 'Incorrect key', 401
    return 'ok', 200


@app.route('/api/v2/stream-schemas', methods=['POST'])
def create_schema_mock():
    schema = request.json
    response = {
        'schema': schema,
        'meta': {
            "createdTime": time.time(),
            "modifiedTime": time.time()
        }
    }
    response['schema']['id'] = f'{schema["name"]}-1234'
    return json.dumps(response)


@app.route('/api/v2/stream-schemas/schemas/<schema_id>', methods=['DELETE'])
def delete_schema_mock(schema_id):
    return json.dumps({'result': 'ok'})


@app.route('/api/v1/status', methods=['GET'])
def status():
    return json.dumps({'result': 'ok'})


@app.route('/api/v2/topology/data', methods=['POST'])
def topology_data():
    if 'type' not in request.args:
        return 'Specify "type"', 400

    with open(os.path.join(OUTPUT_DIR, f'topology_{request.args["type"]}.gz'), 'wb') as f:
        f.write(request.get_data())
    return json.dumps({'result': 'ok'})


@app.route('/api/v2/bc/agents', methods=['POST'])
def bc_pipelines():
    return json.dumps('ok')


@app.route('/api/v2/bc/agents', methods=['DELETE'])
def delete_bc_pipeline():
    return json.dumps('ok')


@app.route('/SolarWinds/InformationService/v3/Json/Query', methods=['GET'])
def solarwinds_data_example():
    if request.headers.get('Authorization') != "Basic QWRtaW46YWRtaW4=":
        return json.dumps({'error': 'Wrong user or pass'}), 401
    predefined_query = 'SELECT TOP 1000 NodeID, DateTime, Archive, MinLoad, MaxLoad, AvgLoad, TotalMemory,' \
                       ' MinMemoryUsed, MaxMemoryUsed, AvgMemoryUsed, AvgPercentMemoryUsed FROM Orion.CPULoad' \
                       ' WHERE DateTime > DateTime(\'2021-03-30T00:00:00Z\')' \
                       ' AND DateTime <= AddSecond(86400, DateTime(\'2021-03-30T00:00:00Z\')) ORDER BY DateTime'

    if "query" in request.args and request.args["query"] == predefined_query:
        with open('data/solarwinds_data_example.json') as f:
            return json.load(f)
    # request is not correct
    return json.dumps({'results': []})


@app.route('/api/v0/devices', methods=['GET'])
def observium_devices():
    # basic auth admin:admin
    if request.headers.get('Authorization') != 'Basic YWRtaW46YWRtaW4=':
        return json.dumps({'error': 'Wrong user or pass'}), 401
    return json.dumps({
        "status": "ok",
        "count": 1,
        "devices": {
            "1": {
                "device_id": "1",
                "poller_id": "0",
                "hostname": "host1",
                "sysName": "sys1",
                "snmp_community": "public",
                "snmp_authlevel": None,
                "snmp_authname": None,
                "snmp_authpass": None,
                "snmp_authalgo": None,
                "snmp_cryptopass": None,
                "snmp_cryptoalgo": None,
                "snmp_context": None,
                "snmp_version": "v2c",
                "snmp_port": "161",
                "snmp_timeout": None,
                "snmp_retries": None,
                "snmp_maxrep": None,
                "ssh_port": "22",
                "agent_version": None,
                "snmp_transport": "udp",
                "bgpLocalAs": "65505",
                "snmpEngineID": "234789798FG43",
                "sysObjectID": ".1.3.6.1.4.1.1.1.2.29",
                "sysDescr": "Juniper Networks, Inc.",
                "sysContact": "Operation Data Team",
                "version": "14.1R7.4",
                "hardware": "HJ73E",
                "vendor": "Juniper",
                "features": "Internet Router",
                "location": "SOME-LOC",
                "os": "alpine",
                "status": "1",
                "status_type": "ok",
                "ignore": "0",
                "ignore_until": None,
                "asset_tag": None,
                "disabled": "0",
                "uptime": "1000",
                "last_rebooted": "1607830000",
                "force_discovery": "0",
                "last_polled": "2021-08-08 00:00:00",
                "last_discovered": "2021-08-08 00:00:00",
                "last_alerter": "2021-08-08 00:00:00",
                "last_polled_timetaken": "22.11",
                "last_discovered_timetaken": "80.21",
                "purpose": None,
                "type": "network",
                "serial": "HSNC749SKN",
                "icon": None,
                "distro": None,
                "distro_ver": None,
                "kernel": None,
                "arch": None,
                "location_id": "2",
                "location_lat": None,
                "location_lon": None,
                "location_country": None,
                "location_state": None,
                "location_county": None,
                "location_city": None,
                "location_geoapi": "geocode",
                "location_status": "Geocoding ENABLED...",
                "location_manual": "0",
                "location_updated": "2021-08-08 00:00:00"
            }
        }
    })


@app.route('/api/v0/ports', methods=['GET'])
def observium_ports():
    # basic auth admin:admin
    if request.headers.get('Authorization') != 'Basic YWRtaW46YWRtaW4=':
        return json.dumps({'error': 'Wrong user or pass'}), 401
    return json.dumps({
        "status": "ok",
        "count": 2,
        "ports": {
            "1": {
                "port_id": "1",
                "device_id": "1",
                "port_64bit": "1",
                "port_label": "fxp0",
                "port_label_base": "fxp",
                "port_label_num": "0",
                "port_label_short": "fxp0",
                "port_descr_type": None,
                "port_descr_descr": None,
                "port_descr_circuit": None,
                "port_descr_speed": None,
                "port_descr_notes": None,
                "ifDescr": "fxp0",
                "ifName": "fxp0",
                "ifIndex": "1",
                "ifSpeed": "10000000",
                "ifConnectorPresent": "true",
                "ifPromiscuousMode": "false",
                "ifHighSpeed": "10",
                "ifOperStatus": "down",
                "ifAdminStatus": "up",
                "ifDuplex": None,
                "ifMtu": "1514",
                "ifType": "ethernetCsmacd",
                "ifAlias": "",
                "ifPhysAddress": "00a0a5744682",
                "ifHardType": None,
                "ifLastChange": "2021-03-31 22:57:53",
                "ifVlan": None,
                "ifTrunk": None,
                "ifVrf": None,
                "encrypted": "0",
                "ignore": "0",
                "disabled": "0",
                "detailed": "0",
                "deleted": "0",
                "ifInUcastPkts": "0",
                "ifInUcastPkts_rate": "0",
                "ifOutUcastPkts": "100500",
                "ifOutUcastPkts_rate": "0",
                "ifInErrors": "0",
                "ifInErrors_rate": "0",
                "ifOutErrors": "0",
                "ifOutErrors_rate": "0",
                "ifOctets_rate": "0",
                "ifUcastPkts_rate": "0",
                "ifErrors_rate": "0",
                "ifInOctets": "0",
                "ifInOctets_rate": "0",
                "ifOutOctets": "0",
                "ifOutOctets_rate": "0",
                "ifInOctets_perc": "0",
                "ifOutOctets_perc": "0",
                "poll_time": "1628160620",
                "poll_period": "299",
                "ifInErrors_delta": "0",
                "ifOutErrors_delta": "0",
                "ifInNUcastPkts": "0",
                "ifInNUcastPkts_rate": "0",
                "ifOutNUcastPkts": "0",
                "ifOutNUcastPkts_rate": "0",
                "ifInBroadcastPkts": "0",
                "ifInBroadcastPkts_rate": "0",
                "ifOutBroadcastPkts": "0",
                "ifOutBroadcastPkts_rate": "0",
                "ifInMulticastPkts": "0",
                "ifInMulticastPkts_rate": "0",
                "ifOutMulticastPkts": "0",
                "ifOutMulticastPkts_rate": "0",
                "port_mcbc": "1",
                "ifInDiscards": "0",
                "ifInDiscards_rate": "0",
                "ifOutDiscards": "0",
                "ifOutDiscards_rate": "0",
                "ifDiscards_rate": "0"
            },
            "2": {
                "port_id": "2",
                "device_id": "1",
                "port_64bit": "1",
                "port_label": "dsc",
                "port_label_base": "dsc",
                "port_label_num": None,
                "port_label_short": "dsc",
                "port_descr_type": None,
                "port_descr_descr": None,
                "port_descr_circuit": None,
                "port_descr_speed": None,
                "port_descr_notes": None,
                "ifDescr": "dsc",
                "ifName": "dsc",
                "ifIndex": "5",
                "ifSpeed": "0",
                "ifConnectorPresent": "false",
                "ifPromiscuousMode": "false",
                "ifHighSpeed": "0",
                "ifOperStatus": "up",
                "ifAdminStatus": "up",
                "ifDuplex": None,
                "ifMtu": "2147483647",
                "ifType": "other",
                "ifAlias": "",
                "ifPhysAddress": None,
                "ifHardType": None,
                "ifLastChange": "2021-03-31 22:57:53",
                "ifVlan": None,
                "ifTrunk": None,
                "ifVrf": None,
                "encrypted": "0",
                "ignore": "0",
                "disabled": "0",
                "detailed": "0",
                "deleted": "0",
                "ifInUcastPkts": "0",
                "ifInUcastPkts_rate": "0",
                "ifOutUcastPkts": "100400",
                "ifOutUcastPkts_rate": "0",
                "ifInErrors": "0",
                "ifInErrors_rate": "0",
                "ifOutErrors": "0",
                "ifOutErrors_rate": "0",
                "ifOctets_rate": "0",
                "ifUcastPkts_rate": "0",
                "ifErrors_rate": "0",
                "ifInOctets": "0",
                "ifInOctets_rate": "0",
                "ifOutOctets": "0",
                "ifOutOctets_rate": "0",
                "ifInOctets_perc": "0",
                "ifOutOctets_perc": "0",
                "poll_time": "1628160620",
                "poll_period": "299",
                "ifInErrors_delta": "0",
                "ifOutErrors_delta": "0",
                "ifInNUcastPkts": "0",
                "ifInNUcastPkts_rate": "0",
                "ifOutNUcastPkts": "0",
                "ifOutNUcastPkts_rate": "0",
                "ifInBroadcastPkts": "0",
                "ifInBroadcastPkts_rate": "0",
                "ifOutBroadcastPkts": "0",
                "ifOutBroadcastPkts_rate": "0",
                "ifInMulticastPkts": "0",
                "ifInMulticastPkts_rate": "0",
                "ifOutMulticastPkts": "0",
                "ifOutMulticastPkts_rate": "0",
                "port_mcbc": "1",
                "ifInDiscards": "0",
                "ifInDiscards_rate": "0",
                "ifOutDiscards": "0",
                "ifOutDiscards_rate": "0",
                "ifDiscards_rate": "0"
            }
        }
    })


@app.route('/api/v0/mempools', methods=['GET'])
def observium_mempools():
    # basic auth admin:admin
    if request.headers.get('Authorization') != 'Basic YWRtaW46YWRtaW4=':
        return json.dumps({'error': 'Wrong user or pass'}), 401
    return json.dumps({
        "vars": [],
        "query": "SELECT *, `mempools`.`mempool_id` AS `mempool_id` FROM `mempools` WHERE 1 AND (( `device_id` IS NOT NULL))  ORDER BY `mempool_descr` ASC",
        "status": "ok",
        "count": 1,
        "entries": {
            "1": {
                "mempool_id": "1",
                "mempool_index": "1253.1",
                "entPhysicalIndex": None,
                "hrDeviceIndex": None,
                "mempool_mib": "CISCO-ENHANCED-MEMPOOL-MIB",
                "mempool_multiplier": "1.00000",
                "mempool_hc": "0",
                "mempool_descr": "Module 1 (Processor)",
                "device_id": "1",
                "mempool_deleted": "0",
                "mempool_warn_limit": None,
                "mempool_crit_limit": None,
                "mempool_ignore": None,
                "mempool_table": "",
                "mempool_polled": "1628160603",
                "mempool_perc": "21",
                "mempool_used": "43289060",
                "mempool_free": "163147772",
                "mempool_total": "206436832"
            }
        }
    })


@app.route('/api/v0/processors', methods=['GET'])
def observium_processors():
    # basic auth admin:admin
    if request.headers.get('Authorization') != 'Basic YWRtaW46YWRtaW4=':
        return json.dumps({'error': 'Wrong user or pass'}), 401
    return json.dumps({
        "status": "ok",
        "count": 1,
        "entries": {
            "1": {
                "processor_id": "1",
                "entPhysicalIndex": "187073",
                "hrDeviceIndex": None,
                "device_id": "1",
                "processor_oid": ".1.3.6.1.4.1.9.9.109.1.1.1.1.8.2082",
                "processor_index": "202",
                "processor_type": "cpm",
                "processor_descr": "description",
                "processor_returns_idle": "0",
                "processor_precision": "1",
                "processor_warn_limit": None,
                "processor_warn_count": None,
                "processor_crit_limit": None,
                "processor_crit_count": None,
                "processor_usage": "3",
                "processor_polled": "1633517705",
                "processor_ignore": "0"
            }
        }
    })


@app.route('/api/v0/storage', methods=['GET'])
def observium_storage():
    # basic auth admin:admin
    if request.headers.get('Authorization') != 'Basic YWRtaW46YWRtaW4=':
        return json.dumps({'error': 'Wrong user or pass'}), 401
    return json.dumps({
        "status": "ok",
        "count": 20,
        "storage": {
            "1": {
                "storage_id": "1",
                "device_id": "1",
                "storage_mib": "HOST-RESOURCES-MIB",
                "storage_index": "1",
                "storage_type": "flashMemory",
                "storage_descr": "description",
                "storage_hc": "0",
                "storage_deleted": "0",
                "storage_warn_limit": None,
                "storage_crit_limit": None,
                "storage_ignore": "0",
                "storage_polled": "1633518002",
                "storage_size": "92762112",
                "storage_units": "2048",
                "storage_used": "47782296",
                "storage_free": "44979816",
                "storage_perc": "52"
            }
        }
    })


if __name__ == '__main__':
    app.run()
