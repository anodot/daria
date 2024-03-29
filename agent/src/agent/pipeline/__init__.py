import agent

from agent import destination
from .pipeline import *
from . import manager
from . import watermark
from . import repository
from . import validators
from . import json_builder
from . import jdbc
from . import exception

TYPES = {
    REGULAR_PIPELINE: Pipeline,
    RAW_PIPELINE: RawPipeline,
    EVENTS_PIPELINE: EventsPipeline,
    TOPOLOGY_PIPELINE: TopologyPipeline,
}


def check_prerequisites() -> list:
    errors = []
    if not destination.repository.exists():
        errors.append('Destination is not configured, please create agent destination first')
    if e := agent.check_streamsets():
        errors.append(e)
    return errors


def check_raw_prerequisites() -> list:
    errors = []
    if e := agent.check_streamsets():
        errors.append(e)
    return errors
