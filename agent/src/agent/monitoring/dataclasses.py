class Sample:
    def __init__(self, name, value, labels, timestamp=None):
        self.name = name
        self.value = value
        self.labels = labels
        self.timestamp = timestamp


class MetricValue:
    def __init__(self):
        self._value = 0.0

    def inc(self, value=1):
        self._value += value

    def dec(self, value=1):
        self._value -= value

    def set(self, value):
        self._value = value

    def get(self):
        return self._value

    @property
    def value(self):
        return self._value


class Metric:
    def __init__(self,
                 name,
                 documentation,
                 labelnames=(),):
        self.name = name
        self.documentation = documentation
        self._labelnames = labelnames
        self._metrics = {}

    def labels(self, *labelvalues, **labelkwargs):
        if labelvalues and labelkwargs:
            raise ValueError("Can't pass both *args and **kwargs")
        if labelkwargs:
            if sorted(labelkwargs) != sorted(self._labelnames):
                raise ValueError('Incorrect label names')
            labelvalues = tuple(labelkwargs[l] for l in self._labelnames)
        else:
            if len(labelvalues) != len(self._labelnames):
                raise ValueError('Incorrect label count')
            labelvalues = tuple(l for l in labelvalues)

        if labelvalues not in self._metrics:
            self._metrics[labelvalues] = MetricValue()

        return self._metrics[labelvalues]

    @property
    def samples(self):
        return [Sample(
            name=self.name,
            value=self._metrics[labelvalues].value,
            labels=dict(zip(self._labelnames, labelvalues)),
        ) for labelvalues in self._metrics]


class Gauge(Metric):
    def __init__(self,
                 name,
                 documentation,
                 labelnames=(), **kwargs):
        super().__init__(
            name=name,
            documentation=documentation,
            labelnames=labelnames,
        )
        self.type = 'gauge'


class Counter(Metric):
    def __init__(self,
                 name,
                 documentation,
                 labelnames=(), **kwargs):
        super().__init__(
            name=name,
            documentation=documentation,
            labelnames=labelnames,
        )
        self.type = 'counter'

    @property
    def samples(self):
        return [Sample(
            name=self.name + '_total',
            value=self._metrics[labelvalues].value,
            labels=dict(zip(self._labelnames, labelvalues)),
        ) for labelvalues in self._metrics]
