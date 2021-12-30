global sdc

try:
    sdc.importLock()
    import sys
    import os
    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import traceback
    from urllib.parse import urlparse
    from influxdb import InfluxDBClient
finally:
    sdc.importUnlock()


def main():
    username = sdc.userParams['USERNAME']
    password = sdc.userParams['PASSWORD']
    host = sdc.userParams['HOST']
    database = sdc.userParams['DATABASE']
    try:
        influx_url_parsed = urlparse(host)
        influx_url = influx_url_parsed.netloc.split(':')
        args = {'host': influx_url[0], 'port': influx_url[1]}
        if username and username != '':
            args['username'] = username
            args['password'] = password
        if influx_url_parsed.scheme == 'https':
            args['ssl'] = True
        if database:
            args['database'] = database
        client = InfluxDBClient(**args)

        if all(db['name'] != database for db in client.get_list_database()):
            raise Exception(f'Database {database} not found. Please check your credentials again')
    except Exception as e:
        sdc.log.error(str(e))
        sdc.log.error(traceback.format_exc())
        raise


main()
