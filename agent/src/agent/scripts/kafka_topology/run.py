import anodot
import argparse
import gzip
import traceback

from agent import destination, monitoring
from agent.modules import proxy, logger
from kafka import KafkaConsumer

logger_ = logger.get_logger('scripts.kafka_topology.run', stdout=True)


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


def run(topic, file_type, brokers: list):
    try:
        destination_ = destination.repository.get()
        api_client = anodot.ApiClient(destination_.access_key,
                                      proxies=proxy.get_config(destination_.proxy),
                                      base_url=destination_.url)
        messages_received = read_data(topic, file_type, brokers)
        if messages_received == 0:
            raise NoDataException(f'Read 0 messages in topic {topic}')

        logger_.info(str(messages_received) + ' messages was read')

        with open(get_file_path(file_type), 'rb') as f_in:
            result = api_client.send_topology_data(file_type, gzip.compress(f_in.read()))
            logger_.info('File sent: ' + str(result))
    except:
        monitoring.metrics.SCHEDULED_SCRIPTS_ERRORS.labels('kafka-to-topology').inc(1)
        logger_.exception(traceback.format_exc())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send data from kafka topic to api/v2/topology/data')
    parser.add_argument('--brokers', default='localhost:9092', help='Kafka brokers connection string')
    parser.add_argument('--topic', help='Topic', required=True)
    parser.add_argument('--type', required=True, help='Can be one of those: ring, zipcode, ncr')

    args = parser.parse_args()
    run(args.topic, args.type, args.brokers.split(','))


class NoDataException(Exception):
    pass
