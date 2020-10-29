from agent import source


def get_errors(query: str):
    errors = []
    if source.JDBCSource.TIMESTAMP_CONDITION not in query:
        errors.append(f'Please add {source.JDBCSource.TIMESTAMP_CONDITION} constant to the query')
    return errors
