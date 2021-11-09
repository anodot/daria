import subprocess


def validate(file: str):
    try:
        subprocess.check_output(['python', '-m', 'py_compile', file], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        print("Status: FAIL", exc.returncode, exc.output)
        raise ValidationException


class ValidationException(Exception):
    pass
