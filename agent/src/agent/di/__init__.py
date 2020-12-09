import inject

from . import source


def init():
    inject.configure(source.config)
