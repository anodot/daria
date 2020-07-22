import argparse
import gzip
import shutil

from agent import destination, anodot_api_client, proxy
from kafka import KafkaConsumer

parser = argparse.ArgumentParser(description='Send data from kafka topic to api/v2/topology/data')
parser.add_argument('--brokers', default='localhost:9092', help='Kafka brokers connection string')
parser.add_argument('--topic', help='Topic', required=True)
parser.add_argument('--type', required=True, help='Can be one of those: ring, zipcode, ncr')

args = parser.parse_args()

consumer = KafkaConsumer(args.topic,
                         group_id='anodot_topology',
                         bootstrap_servers=args.brokers.split(','),
                         value_deserializer=lambda m: m.decode('utf-8'),
                         consumer_timeout_ms=5000,
                         auto_offset_reset='earliest',
                         enable_auto_commit=False)

count_messages = 0
with open(f'/tmp/{args.type}', 'w') as f:
    for msg in consumer:
        f.write(msg.value)
        f.write('\n')
        count_messages += 1

print(str(count_messages) + ' messages was read')

destination_ = destination.HttpDestination.get()
api_client = anodot_api_client.AnodotApiClient(destination_.access_key,
                                               proxies=proxy.get_config(destination_.proxy),
                                               base_url=destination_.url)

with open(f'/tmp/{args.type}', 'rb') as f_in:
    api_client.send_topology_data(args.type, gzip.compress(f_in.read()))



