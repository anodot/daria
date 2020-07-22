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
                         consumer_timeout_ms=1000)

count_messages = 0
with open(f'/tmp/{args.type}', 'w') as f:
    for msg in consumer:
        f.write(msg.value)
        f.write('\n')
        count_messages += 1

    with gzip.open(f'/tmp/{args.type}.gz', 'w') as f_out:
        shutil.copyfileobj(f, f_out)

destination_ = destination.HttpDestination.get()
api_client = anodot_api_client.AnodotApiClient(destination_.access_key,
                                               proxies=proxy.get_config(destination_.proxy),
                                               base_url=destination_.url)

with gzip.open(f'/tmp/{args.type}.gz', 'rb') as f_out:
    api_client.send_topology_data(f_out.read())



