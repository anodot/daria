from abc import ABC, abstractmethod


class KafkaExtractor:
    def get(self):
        # getting data from kafka
        return


class MongoExtractor:
    def get(self):
        # getting data from mongo
        return


class Source(ABC):
    @abstractmethod
    def get_data(self):
        pass

    def transform(self):
        self.get_data()
        # do smth


class MongoSource(Source):
    def get_data(self):
        return MongoExtractor().get()


class KafkaSource(Source):
    def get_data(self):
        return KafkaExtractor().get()
