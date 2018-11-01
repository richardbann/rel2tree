from collections import namedtuple
from .core import Convert, const, GroupBy, GroupKey


class Const(Convert):
    def __init__(self, value):
        super().__init__(const(value))


def field(d):
    def fnc(x):
        return x[d]
    return fnc


class SumField(Convert):
    def __init__(self, _field, **kwargs):
        super().__init__(lambda x: sum(map(field(_field), x)), **kwargs)


class MinField(Convert):
    def __init__(self, _field, **kwargs):
        super().__init__(lambda x: min(map(field(_field), x)), **kwargs)


class MaxField(Convert):
    def __init__(self, _field, **kwargs):
        super().__init__(lambda x: max(map(field(_field), x)), **kwargs)


class AvgField(Convert):
    def __init__(self, _field, **kwargs):
        super().__init__(
            lambda x: sum(map(field(_field), x)) / len(x), **kwargs
        )


class GroupKeyField(GroupKey):
    def __init__(self, field):
        super().__init__(lambda x: getattr(x, field))


class GroupByFields(GroupBy):
    def __init__(self, fields, groupconvert, **kwargs):
        Key = namedtuple('Key', fields)
        super().__init__(
            lambda x: Key(*[x.get(f) for f in fields]),
            groupconvert,
            **kwargs
        )
