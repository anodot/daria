import click
import re

from .abstract_source import Source, SourceException
from agent.tools import infinite_retry
from pymongo import MongoClient


class MonitoringSource(Source):
    def prompt(self, default_config, advanced=False):
        pass
