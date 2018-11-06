from collections import namedtuple

from .core import Aggregator, GroupBy


def field(d):
    def fnc(x):
        return x[d]
    return fnc


def const(d):
    def fnc(x):
        return d
    return fnc


class Const(Aggregator):
    def __init__(self, value):
        super().__init__(const(value))


class SumField(Aggregator):
    def __init__(self, _field, **kwargs):
        super().__init__(lambda x: sum(map(field(_field), x)), **kwargs)


class MinField(Aggregator):
    def __init__(self, _field, **kwargs):
        super().__init__(lambda x: min(map(field(_field), x)), **kwargs)


class MaxField(Aggregator):
    def __init__(self, _field, **kwargs):
        super().__init__(lambda x: max(map(field(_field), x)), **kwargs)


class AvgField(Aggregator):
    def __init__(self, _field, **kwargs):
        super().__init__(
            lambda x: sum(map(field(_field), x)) / len(x), **kwargs
        )


class FirstField(Aggregator):
    def __init__(self, field):
        super().__init__(lambda x: x[0][field])


class GroupByFields(GroupBy):
    def __init__(self, fields, aggregator, **kwargs):
        Key = namedtuple('Key', fields)
        super().__init__(
            lambda x: Key(*[x.get(f) for f in fields]),
            aggregator,
            **kwargs
        )
