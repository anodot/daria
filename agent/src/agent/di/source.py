from agent.pipeline.validators.source import SourceConnectionValidator


def config(binder):
    binder.bind(SourceConnectionValidator, SourceConnectionValidator())
