import sdc_client

from agent import streamsets


def config(binder):
    binder.bind(sdc_client.IStreamSetsProvider, streamsets.Provider())
