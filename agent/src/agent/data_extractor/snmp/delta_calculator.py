class DeltaCalculator:
    def __init__(self):
        self._values = {}

    def delta(self, key, value):
        last = self._values.get(key)
        self._values[key] = value
        if last is None:
            return None
        return value - last
