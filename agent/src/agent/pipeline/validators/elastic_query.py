import re


def get_errors(query: str, offset_field: str):
    errors = []
    if not is_valid_timestamp(query, offset_field):
        errors.append(f'The query must have ascending ordering by the `{offset_field}`')
    if not is_valid_offset(query):
        errors.append('Please use ${OFFSET} with a gt condition (not gte)')
    return errors


def is_valid_timestamp(query: str, offset_field: str) -> bool:
    regexp = re.compile(rf'"sort"[\s\S]*"{offset_field}"[\s\S]*"order"[\s\S]*"asc"')
    if regexp.search(query):
        return True
    return False


def is_valid_offset(query: str) -> bool:
    regexp = re.compile(r'"gt"[\s\S]*\${OFFSET}')
    if regexp.search(query):
        return True
    return False
