import inject

from . import source


def init():
    inject.configure_once(source.config)
