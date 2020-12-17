import inject
import sdc_client

from . import source, pipeline, streamsets
from agent.modules.logger import get_logger


def config(binder):
    binder.install(source.config)
    binder.install(pipeline.config)
    binder.install(streamsets.config)
    binder.bind(sdc_client.ILogger, get_logger('sdc_client'))


def init():
    inject.configure_once(config)
