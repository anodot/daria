import csv

from . import condition


def validate_file(file):
    with open(file, 'r') as f:
        for row in csv.DictReader(f, fieldnames=['result', 'value', 'condition']):
            if len(row) < 2:
                raise TransformationException('Wrong csv format. Missing fields')
            condition.validate_value(row['value'])
            if row['condition']:
                condition.validate(row['condition'])


class TransformationException(Exception):
    pass
