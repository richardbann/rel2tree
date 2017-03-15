from .core import AggregatorBase, GroupBy, Constant, Sortable


class Aggregator(AggregatorBase):
    pass


class GroupingField(Constant):
    pass


class Sum(AggregatorBase):
    _initial = 0

    def _aggregator(self, acc, item):
        return acc + item


class SumField(AggregatorBase):
    _initial = 0

    def _aggregator(self, acc, item):
        return acc + item[self._field_name]

    def __init__(self, field_name, **kwargs):
        self._field_name = field_name
        super(SumField, self).__init__(**kwargs)


class ExtractField(SumField):
    _initial = None

    def _aggregator(self, acc, item):
        return item[self._field_name]


class SimpleList(Sortable):
    _initial = []

    def _aggregator(self, acc, item):
        acc.append(item)
        return acc

    def __len__(self):
        return len(self._value())

    def __iter__(self):
        return self._value().__iter__()


class List(GroupBy):
    def _grouping(self, record):
        ret = self.cnt
        self.cnt += 1
        return ret

    def __init__(self, **kwargs):
        self.cnt = 0
        super(List, self).__init__(**kwargs)

    def _add_const_fields(self, kwargs, key):
        pass

    def _get(self, idx):
        return self._internal_value[idx]


class GroupByFields(GroupBy):
    def _grouping(self, record):
        return tuple([record[k] for k in self._grouping_fields])

    def __init__(self, **kwargs):
        self._grouping_fields = [k for k, v in kwargs.items()
                                 if isinstance(v, GroupingField)]
        super(GroupByFields, self).__init__(**kwargs)

    def _add_const_fields(self, kwargs, key):
        for i, field in enumerate(self._grouping_fields):
            kwargs[field]._set_value(key[i])
