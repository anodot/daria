from agent import pipeline


def get_errors(query: str):
    errors = []
    if pipeline.jdbc.query.TIMESTAMP_CONDITION not in query:
        errors.append(f'Please add {pipeline.jdbc.query.TIMESTAMP_CONDITION} constant to the query')
    return errors
