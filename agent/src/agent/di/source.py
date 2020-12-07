from agent import source, pipeline


def config(binder):
    binder.bind(source.validator.IConnectionValidator, pipeline.validators.source.SourceConnectionValidator())
