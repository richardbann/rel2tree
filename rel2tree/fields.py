from .core import Field, GroupBy


class Const(Field):
    def __init__(self, const):
        self._const = const

    def feed(self, iterable):
        pass

    def get(self):
        return self._const


class FieldAggregator(Field):
    listaggregator = None

    def __init__(self, fieldname, **kwargs):
        super().__init__(**kwargs)

        def _aggr(lst):
            return self.listaggregator([r[fieldname] for r in lst])

        self._aggregator = _aggr


class SumField(FieldAggregator):
    listaggregator = sum


class MaxField(FieldAggregator):
    listaggregator = max


class MinField(FieldAggregator):
    listaggregator = min


class PickField(Field):
    def __init__(self, fieldname, **kwargs):
        super().__init__(**kwargs)
        self._aggregator = lambda lst: lst[0][fieldname] if lst else None


class GroupByFields(GroupBy):
    def __init__(self, fieldnames, **kwargs):
        super().__init__(**kwargs)
        if isinstance(fieldnames, str):
            fieldnames = (fieldnames,)
        self._groupkey = lambda r: tuple(r[fn] for fn in fieldnames)
