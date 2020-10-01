from urllib.parse import urlparse
from influxdb import InfluxDBClient
from pymongo import MongoClient


def get_influx_client(host, username=None, password=None, db=None) -> InfluxDBClient:
    influx_url_parsed = urlparse(host)
    influx_url = influx_url_parsed.netloc.split(':')
    args = {'host': influx_url[0], 'port': influx_url[1]}
    if username and username != '':
        args['username'] = username
        args['password'] = password
    if influx_url_parsed.scheme == 'https':
        args['ssl'] = True
    if db:
        args['database'] = db
    return InfluxDBClient(**args)


def get_mongo_client(connection_string: str, username: str, password: str, auth_source: str) -> MongoClient:
    args = {}
    if username:
        args['authSource'] = auth_source
        args['username'] = username
        args['password'] = password
    return MongoClient(connection_string, **args)
