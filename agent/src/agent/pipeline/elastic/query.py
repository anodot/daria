import re

OFFSET = '${OFFSET}'


class Validator:
    @staticmethod
    def get_errors(query: str, offset_field: str):
        errors = []
        if not Validator.__is_valid_timestamp(query, offset_field):
            errors.append(f'The cls should have ascending ordering by {offset_field}')
        if not Validator.__is_valid_offset(query):
            errors.append('Please use ${OFFSET} with a gt condition (not gte)')
        return errors

    @staticmethod
    def __is_valid_timestamp(query: str, offset_field: str) -> bool:
        regexp = re.compile(rf'"sort"[\s\S]*"{offset_field}"[\s\S]*"order"[\s\S]*"asc"')
        if regexp.search(query):
            return True
        return False

    @staticmethod
    def __is_valid_offset(query: str) -> bool:
        # TODO offset
        regexp = re.compile(r'"gt"[\s\S]*\${OFFSET}')
        if regexp.search(query):
            return True
        return False
