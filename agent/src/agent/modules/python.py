import subprocess


def validate(file: str):
    try:
        subprocess.check_output(['python', '-m', 'py_compile', file], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        raise ValidationException(e.output)


class ValidationException(Exception):
    pass
