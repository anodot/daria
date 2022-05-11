from agent.pipeline.jdbc.query import TIMESTAMP_CONDITION, TIMESTAMP_COLUMN, LAST_TIMESTAMP_VALUE, INTERVAL


def get_errors(query: str):
    errors = []
    if TIMESTAMP_CONDITION not in query:
        errors.append(f'Please add {TIMESTAMP_CONDITION} constant to the query')
        if any(i not in query for i in [TIMESTAMP_COLUMN, LAST_TIMESTAMP_VALUE, INTERVAL]):
            errors.append(f'Please add {LAST_TIMESTAMP_VALUE}, {LAST_TIMESTAMP_VALUE}, {INTERVAL} constants to the query')
        else:
            errors.pop()
    return errors
