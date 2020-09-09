import anodot
import argparse
import gzip
import logging
import sys

from agent import destination, proxy, logger
from datetime import datetime
from kafka import KafkaConsumer

logger_ = logger.get_logger('scripts.kafka_topology.run')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger_.addHandler(handler)


def get_file_path(name):
    return f'/tmp/{name}'


def read_data(topic, file_type, brokers: list) -> int:
    consumer = KafkaConsumer(topic,
                             group_id='anodot_topology',
                             bootstrap_servers=brokers,
                             value_deserializer=lambda m: m.decode('utf-8'),
                             consumer_timeout_ms=5000,
                             auto_offset_reset='earliest',
                             enable_auto_commit=False)

    count_messages = 0
    with open(get_file_path(file_type), 'w') as f:
        for msg in consumer:
            f.write(msg.value)
            f.write('\n')
            count_messages += 1

    return count_messages


def send_monitoring_metric(what, value, destination_, file_type):
    anodot.send([anodot.Metric20(what=what,
                                 value=value,
                                 target_type=anodot.TargetType.GAUGE,
                                 timestamp=datetime.now(),
                                 dimensions={'source': 'kafka_to_topology_monitoring', 'file_type': file_type})],
                token=destination_.token,
                logger=logger_,
                base_url=destination_.url)


def run(topic, file_type, brokers: list):
    destination_ = destination.repository.get()
    api_client = anodot.ApiClient(destination_.access_key,
                                  proxies=proxy.get_config(destination_.proxy),
                                  base_url=destination_.url)
    messages_received = read_data(topic, file_type, brokers)
    send_monitoring_metric('messages_read', messages_received, destination_, file_type)

    logger_.info(str(messages_received) + ' messages was read')

    with open(get_file_path(file_type), 'rb') as f_in:
        result = api_client.send_topology_data(file_type, gzip.compress(f_in.read()))
        send_monitoring_metric('messages_sent', messages_received, destination_, file_type)
        logger_.info('File sent: ' + str(result))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send data from kafka topic to api/v2/topology/data')
    parser.add_argument('--brokers', default='localhost:9092', help='Kafka brokers connection string')
    parser.add_argument('--topic', help='Topic', required=True)
    parser.add_argument('--type', required=True, help='Can be one of those: ring, zipcode, ncr')

    args = parser.parse_args()
    try:
        run(args.topic, args.type, args.brokers.split(','))
    except Exception:
        logger_.exception('Uncaught exception')
