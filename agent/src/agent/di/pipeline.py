import sdc_client

from agent import pipeline


def config(binder):
    binder.bind(sdc_client.IPipelineProvider, pipeline.Provider())
