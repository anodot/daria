import csv

from . import condition


def validate_file(file):
    with open(file, 'r') as f:
        for row in csv.DictReader(f, fieldnames=['result', 'value', 'condition']):
            if len(row) < 3:
                raise TransformationException('Wrong csv format. Missing fields')
            if row['condition']:
                condition.validate(row['condition'])


class TransformationException(Exception):
    pass
