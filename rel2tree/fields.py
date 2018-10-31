from collections import namedtuple
from .core import Aggregator, GroupBy, GroupKey


class SumField(Aggregator):
    def __init__(self, fieldname, **kwargs):
        super().__init__(lambda x: sum([f[fieldname] for f in x]), **kwargs)


class MinField(Aggregator):
    def __init__(self, fieldname, **kwargs):
        super().__init__(lambda x: min([f[fieldname] for f in x]), **kwargs)


class MaxField(Aggregator):
    def __init__(self, field, **kwargs):
        super().__init__(lambda x: max([f[field] for f in x]), **kwargs)


class AvgField(Aggregator):
    def __init__(self, field, **kwargs):
        super().__init__(
            lambda x: sum([f[field] for f in x]) / len(x), **kwargs
        )


class List(Aggregator):
    def __init__(self, fnc, **kwargs):
        super().__init__(lambda x: [fnc(f) for f in x], **kwargs)


class ListFields(List):
    def __init__(self, fields, **kwargs):
        super().__init__(lambda x: {f: x[f] for f in fields}, **kwargs)


class GroupKeyField(GroupKey):
    def __init__(self, field):
        super().__init__(lambda x: getattr(x, field))


class GroupByFields(GroupBy):
    def __init__(self, fields, aggregator, **kwargs):
        Key = namedtuple('Key', fields)
        super().__init__(
            aggregator,
            lambda x: Key(*[x.get(f) for f in fields]),
            **kwargs
        )
