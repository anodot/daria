from agent.pipeline.jdbc.query import TIMESTAMP_CONDITION, TIMESTAMP_COLUMN, LAST_TIMESTAMP_VALUE, INTERVAL


def get_errors(query: str):
    errors = []
    if TIMESTAMP_CONDITION not in query and \
            any(i not in query for i in [TIMESTAMP_COLUMN, LAST_TIMESTAMP_VALUE, INTERVAL]):
        errors.append(f'Please add either {TIMESTAMP_CONDITION} constant or '
                      f'all of the following {LAST_TIMESTAMP_VALUE}, {LAST_TIMESTAMP_VALUE}, {INTERVAL} to the query')
    return errors
