from abc import ABC, abstractmethod


class KafkaExtractor:
    def get(self):
        con = get_kafka_consumer()
        return con.consume()


class MongoExtractor:
    def get(self):
        conn = connect_to_mongo()
        return conn.query()


class Source(ABC):
    @abstractmethod
    def get_data(self):
        pass

    def transform(self):
        data = self.get_data()
        # 
        # transform data for sending
        #
        return data


class MongoSource(Source):
    def get_data(self):
        return MongoExtractor().get()


class KafkaSource(Source):
    def get_data(self):
        return KafkaExtractor().get()
    
    
kafka_source = KafkaSource()
kafka_data = kafka_source.transform()
send(kafka_data)

mongo_source = MongoSource()
mongo_data = mongo_source.transform()
send(mongo_data)

