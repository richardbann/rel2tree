# TODO: magic: len, iter, etc.
# TODO: List and GroupBy ordering

import copy
from collections import OrderedDict


class ComputationError(Exception):
    pass


class AggregatorBase(object):
    _creation_counter = 0

    def _set_if_missing(self, kwargs, attrname):
        if not hasattr(self, attrname):
            setattr(self, attrname, kwargs.pop(attrname, None))

    def _get_initial(self):
        return copy.copy(self._initial)

    def __init__(self, **kwargs):
        self._creation_counter = AggregatorBase._creation_counter
        AggregatorBase._creation_counter += 1
        self._set_if_missing(kwargs, '_initial')
        self._set_if_missing(kwargs, '_aggregator')
        self._set_if_missing(kwargs, '_prefilter')
        if kwargs:
            msg = ', '.join(['%s: %s' % (k, v) for k, v in kwargs.items()])
            msg = 'Invalid fields in Aggregator: %s' % msg
            raise TypeError(msg)
        self._internal_value = self._get_initial()

    def _aggregate(self, item):
        if self._aggregator:
            val = self._aggregator(self._internal_value, item)
            self._internal_value = val

    def _feed(self, item):
        if not self._prefilter or self._prefilter(item):
            self._aggregate(item)
        return self

    def _feedmany(self, records):
        for record in records:
            self._feed(record)
        return self

    def _value(self):
        return self._internal_value

    def _json(self):
        return self._value()


class Computed(AggregatorBase):
    def __init__(self, fnc):
        self._fnc = fnc
        super(Computed, self).__init__()

    def _compute(self, parent):
        self._internal_value = self._fnc(parent)
        return self


class Constant(AggregatorBase):
    def __init__(self, value=None):
        super(Constant, self).__init__()
        self._set_value(value)

    def _set_value(self, value):
        self._internal_value = value


class GroupingField(Constant):
    pass


class Aggregator(AggregatorBase):
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


class SimpleList(AggregatorBase):
    _initial = []

    def _aggregator(self, acc, item):
        acc.append(item)
        return acc


class Struct(AggregatorBase):
    def __init__(self, **kwargs):
        self._aggregator_fields = {}
        self._computed_fields = {}
        flds = []
        for field_name in list(kwargs):
            val = kwargs[field_name]
            if isinstance(val, AggregatorBase):
                flds.append((field_name, val))
                kwargs.pop(field_name)
                if isinstance(val, Computed):
                    self._computed_fields[field_name] = val
                else:
                    self._aggregator_fields[field_name] = val
        flds.sort(key=lambda f: f[1]._creation_counter)
        self._sorted_fields = flds
        super(Struct, self).__init__(**kwargs)

    def _get_initial(self):
        return copy.deepcopy(self._aggregator_fields)

    def _aggregate(self, record):
        for field_name in self._aggregator_fields:
            self._internal_value[field_name]._feed(record)

    def __getattr__(self, field_name):
        if field_name[0] != '_':
            if field_name in self._aggregator_fields:
                return self._internal_value[field_name]
            if field_name in self._computed_fields:
                return self._computed_fields[field_name]._compute(self)
        msg = '%s object has no attribute %s'
        raise AttributeError(msg % (type(self).__name__, field_name))

    def _value(self):
        flds = [(f, getattr(self, f)) for f, _ in self._sorted_fields]
        return OrderedDict(flds)


class GroupBy(Struct):
    def __init__(self, **kwargs):
        self._set_if_missing(kwargs, '_grouping')
        self._set_if_missing(kwargs, '_postfilter')
        super(GroupBy, self).__init__(**kwargs)

    def _get_initial(self):
        return OrderedDict()  # preserve insertion order

    def _add_const_fields(self, kwargs, key):
        kwargs.update({'groupKey': Constant(key)})

    def _get_key(self, record):
        return self._grouping(record) if self._grouping else None

    def _aggregate(self, record):
        key = self._get_key(record)
        try:
            bucket = self._internal_value[key]
        except KeyError:
            kw = dict(self._sorted_fields)
            self._add_const_fields(kw, key)
            bucket = Struct(**kw)
            self._internal_value[key] = bucket
        bucket._feed(record)

    def _get(self, record):
        key = self._get_key(record)
        return self._internal_value[key]

    def _value(self):
        if self._postfilter:
            return [r for r in self._internal_value.values()
                    if self._postfilter(r)]
        return list(self._internal_value.values())  # TODO: list?


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
