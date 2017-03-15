import copy
from collections import OrderedDict


class ComputationError(Exception):
    pass


class AggregatorBase(object):
    _creation_counter = 0

    def _ensure_attr(self, kwargs, attrname):
        if attrname in kwargs:
            setattr(self, attrname, kwargs.pop(attrname))
        elif not hasattr(self, attrname):
            setattr(self, attrname, None)

    def _get_initial(self):
        return copy.copy(self._initial)

    def __init__(self, **kwargs):
        self._creation_counter = AggregatorBase._creation_counter
        AggregatorBase._creation_counter += 1
        self._ensure_attr(kwargs, '_initial')
        self._ensure_attr(kwargs, '_aggregator')
        self._ensure_attr(kwargs, '_prefilter')
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

    def __bool__(self):
        return bool(self._value())
    __nonzero__ = __bool__


class Sortable(AggregatorBase):
    def __init__(self, **kwargs):
        self._ensure_attr(kwargs, '_sortkey')
        super(Sortable, self).__init__(**kwargs)

    def _value(self):
        ret = super(Sortable, self)._value()
        if self._sortkey:
            ret.sort(key=self._sortkey)
        return ret


class Computed(Sortable, AggregatorBase):
    def __init__(self, fnc, **kwargs):
        self._fnc = fnc
        super(Computed, self).__init__(**kwargs)

    def _compute(self, parent):
        self._internal_value = self._fnc(parent)
        return self


class Constant(AggregatorBase):
    def __init__(self, value=None):
        super(Constant, self).__init__()
        self._set_value(value)

    def _set_value(self, value):
        self._internal_value = value


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

    def __len__(self):
        return len(self._value())

    def __iter__(self):
        return self._value().__iter__()


class GroupByBase(Struct):
    def __init__(self, **kwargs):
        self._ensure_attr(kwargs, '_grouping')
        self._ensure_attr(kwargs, '_postfilter')
        super(GroupByBase, self).__init__(**kwargs)

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
        return list(self._internal_value.values())


class GroupBy(Sortable, GroupByBase):
    pass
