class Interval:
    MIN_1 = '1m'
    MIN_5 = '5m'
    HOUR_1 = '1h'
    DAY_1 = '1d'
    WEEK_1 = '1w'

    VALUES = [MIN_1, MIN_5, HOUR_1, DAY_1, WEEK_1]

    def __init__(self, value: str):
        if value not in self.VALUES:
            raise Exception("Invalid value supplied")
        self.value = value

    def total_seconds(self):
        if self.value == self.MIN_1:
            return 60
        if self.value == self.MIN_5:
            return 60 * 5
        if self.value == self.HOUR_1:
            return 60 * 60
        if self.value == self.DAY_1:
            return 60 * 60 * 24
        if self.value == self.WEEK_1:
            return 60 * 60 * 24 * 7
