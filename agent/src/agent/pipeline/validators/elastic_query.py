import re


def get_errors(query: str, offset_field: str, schema: bool):
    errors = []
    if not is_valid_timestamp(query, offset_field):
        errors.append(f'The query must have ascending ordering by the `{offset_field}`')
    if schema:
        if not is_valid_schema_offset(query):
            errors.append('Please use "$OFFSET" with a gte condition (not gt), and $OFFSET+$INTERVAL with lt condition')
    elif not is_valid_offset(query):
        errors.append('Please use ${OFFSET} with a gt condition (not gte)')
    return errors


def is_valid_timestamp(query: str, offset_field: str) -> bool:
    regexp = re.compile(rf'"sort"[\s\S]*"{offset_field}"[\s\S]*"order"[\s\S]*"asc"')
    if regexp.search(query):
        return True
    return False


def is_valid_schema_offset(query: str) -> bool:
    regex_gte = re.compile(r'"gte"[\s\S]*\$OFFSET')
    regex_lt = re.compile(r'"lt"[\s\S]*\$OFFSET+\+\$INTERVAL')
    return bool(regex_gte.search(query) and regex_lt.search(query))


def is_valid_offset(query: str) -> bool:
    regexp = re.compile(r'"gt"[\s\S]*\${OFFSET}')
    if regexp.search(query):
        return True
    return False
