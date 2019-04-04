from .config_handlers.json import JsonConfigHandler
from .config_handlers.influx import InfluxConfigHandler
from .config_handlers.kafka import KafkaConfigHandler
from .prompt import PromptConfigMongo, PromptConfigKafka, PromptConfigInflux


class Pipeline:
    def __init__(self, prompt_class, config_handler_class):
        self.prompt_class = prompt_class
        self.config_handler_class = config_handler_class

    def prompt(self, default_config, advanced):
        return self.prompt_class(default_config, advanced).config

    def get_config_handler(self, pipeline_config, base_config=None):
        return self.config_handler_class(pipeline_config, base_config)


pipeline_configs = {
    'mongo': Pipeline(PromptConfigMongo, JsonConfigHandler),
    'kafka': Pipeline(PromptConfigKafka, KafkaConfigHandler),
    'influx': Pipeline(PromptConfigInflux, InfluxConfigHandler),
}
