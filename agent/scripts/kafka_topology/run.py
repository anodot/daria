import argparse
import gzip
import logging
import sys

from agent import destination, anodot_api_client, proxy, logger
from kafka import KafkaConsumer

logger_ = logger.get_logger('scripts.kafka_topology.run')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger_.addHandler(handler)

parser = argparse.ArgumentParser(description='Send data from kafka topic to api/v2/topology/data')
parser.add_argument('--brokers', default='localhost:9092', help='Kafka brokers connection string')
parser.add_argument('--topic', help='Topic', required=True)
parser.add_argument('--type', required=True, help='Can be one of those: ring, zipcode, ncr')

args = parser.parse_args()


def get_file_path(name):
    return f'/tmp/{name}'


def read_data(topic, file_type) -> int:
    consumer = KafkaConsumer(topic,
                             group_id='anodot_topology',
                             bootstrap_servers=args.brokers.split(','),
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


def send_file(file_type):
    with open(get_file_path(file_type), 'rb') as f_in:
        res = api_client.send_topology_data(args.type, gzip.compress(f_in.read()))

    return res


try:
    destination_ = destination.HttpDestination.get()
    api_client = anodot_api_client.AnodotApiClient(destination_.access_key,
                                                   proxies=proxy.get_config(destination_.proxy),
                                                   base_url=destination_.url)
    messages_received = read_data(args.topic, args.type)
    logger_.info(str(messages_received) + ' messages was read')

    result = send_file(args.type)
    logger_.info('File sent: ' + str(result))
except Exception:
    logger_.exception('Uncaught exception')
