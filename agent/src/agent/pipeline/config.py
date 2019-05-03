from .config_handlers.json import JsonConfigHandler
from .config_handlers.influx import InfluxConfigHandler
from .config_handlers.kafka import KafkaConfigHandler
from .prompt import PromptConfigMongo, PromptConfigKafka, PromptConfigInflux
from .load_client_data import InfluxLoadClientData, KafkaLoadClientData, MongoLoadClientData


class Pipeline:
    def __init__(self, prompt_class, config_handler_class, load_class):
        self.prompt_class = prompt_class
        self.config_handler_class = config_handler_class
        self.load_class = load_class

    def prompt(self, default_config, advanced):
        return self.prompt_class(default_config, advanced).config

    def get_config_handler(self, pipeline_config, base_config=None):
        return self.config_handler_class(pipeline_config, base_config)

    def load(self, client_config, source_type, edit=False):
        return self.load_class(client_config, source_type, edit).load()


pipeline_configs = {
    'mongo': Pipeline(PromptConfigMongo, JsonConfigHandler, MongoLoadClientData),
    'kafka': Pipeline(PromptConfigKafka, KafkaConfigHandler, KafkaLoadClientData),
    'influx': Pipeline(PromptConfigInflux, InfluxConfigHandler, InfluxLoadClientData),
}
