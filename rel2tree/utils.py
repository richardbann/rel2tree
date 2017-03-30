from .core import AggregatorBase, SortingMixin, HavingMixin, GroupBy


class Sum(AggregatorBase):
    def _aggregator(self, records, inner):
        return sum(records)


class FieldAggregator(AggregatorBase):
    def __init__(self, field_name, **kwargs):
        self.field_name = field_name
        super(FieldAggregator, self).__init__(**kwargs)


class GroupingField(FieldAggregator):
    def _aggregator(self, records, inner):
        if records:
            return records[0].get(self.field_name)
        return None


class SumField(FieldAggregator):
    def _aggregator(self, records, inner):
        return sum([r.get(self.field_name) for r in records])


class FirstField(GroupingField):
    pass


class List(SortingMixin, HavingMixin, AggregatorBase):
    pass


class GroupByFields(GroupBy):
    def __init__(self, **kwargs):
        super(GroupByFields, self).__init__(**kwargs)
        gf = [b.field_name for a, b in self._fields
              if isinstance(b, GroupingField)]
        self._grouping_fields = gf

    def _grouping(self, record):
        return tuple([record.get(x) for x in self._grouping_fields])
