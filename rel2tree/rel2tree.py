import copy
from collections import OrderedDict


class ComputationError(Exception):
    pass


class DataClass(object):
    def __init__(self, **kwargs):
        json_fields = []
        for k, v in kwargs.items():
            json_fields.append((k, k))
            setattr(self, k, v)
        self._json_fields = json_fields


class Computed(object):
    def __init__(self, fnc):
        self._fnc = fnc


class AggregatorBase(object):
    _internal_value = None
    _prefilter = None

    @staticmethod
    def _aggregator(v, obj):
        pass  # pragma: no cover

    def _aggregate(self, obj):
        self._internal_value = self._aggregator(self._internal_value, obj)

    def _feed(self, *args, **kwargs):
        obj = args[0] if args else DataClass(**kwargs)
        return self._feedobject(obj)

    def _feedobject(self, obj):
        if not self._prefilter or self._prefilter(obj):
            self._aggregate(obj)
        return self

    def _feedmany(self, objects):
        for obj in objects:
            self._feedobject(obj)
        return self

    def _value(self):
        return self._internal_value

    def __len__(self):
        return len(self._value())

    def _json(self):
        return self._value()


class Aggregator(AggregatorBase):
    def __init__(self, initial, aggregator, _prefilter=None):
        self._internal_value = initial
        self._aggregator = aggregator
        self._prefilter = _prefilter


class SumField(Aggregator):
    def __init__(self, field_name, _prefilter=None):
        def aggregator(v, obj):
            return v + getattr(obj, field_name)
        super(SumField, self).__init__(0, aggregator, _prefilter)


class List(AggregatorBase):
    def __init__(self, _prefilter=None):
        self._prefilter = _prefilter
        self._internal_value = []

    @staticmethod
    def _aggregator(v, obj):
        v.append(obj)
        return v


class Struct(AggregatorBase):
    def __init__(self, **kwargs):
        self._prefilter = kwargs.pop('_prefilter', None)
        self._aggregator_fields = {}
        self._computed_fields = {}
        self._other_fields = {}
        self._all_fields = list(kwargs.keys())
        for k, v in kwargs.items():
            if isinstance(v, AggregatorBase):
                self._aggregator_fields[k] = v
            elif isinstance(v, Computed):
                self._computed_fields[k] = v
            else:
                self._other_fields[k] = v
        self._internal_value = self._get_initial_value()

    def _get_initial_value(self):
        return copy.deepcopy(self._aggregator_fields)

    def _aggregate(self, obj):
        for field_name in self._aggregator_fields:
            self._internal_value[field_name]._feedobject(obj)

    def __getattr__(self, field_name):
        if field_name[0] != '_':
            if field_name in self._aggregator_fields:
                return self._internal_value[field_name]
            if field_name in self._computed_fields:
                return self._computed_fields[field_name]._fnc(self)
            if field_name in self._other_fields:
                return self._other_fields[field_name]
        msg = '%s object has no attribute %s'
        raise AttributeError(msg % (type(self).__name__, field_name))

    def _value(self):
        return {field: getattr(self, field) for field in self._all_fields}


class GroupBy(Struct):
    def __init__(self, **kwargs):
        self._grouping = kwargs.pop('_grouping', None)
        self._postfilter = kwargs.pop('_postfilter', None)
        self._fields = kwargs
        super(GroupBy, self).__init__(**kwargs)

    def _get_initial_value(self):
        return OrderedDict()

    def _get_const_fields(self, key):
        return {'groupKey': key}

    def _get_key(self, obj):
        return self._grouping(obj) if self._grouping else None

    def _aggregate(self, obj):
        key = self._get_key(obj)
        try:
            bucket = self._internal_value[key]
        except KeyError:
            kwargs = self._fields.copy()
            kwargs.update(self._get_const_fields(key))
            bucket = Struct(**kwargs)
            self._internal_value[key] = bucket
        bucket._feedobject(obj)

    def _get(self, obj):
        key = self._get_key(obj)
        return self._internal_value[key]

    def _value(self):
        if self._postfilter:
            return [r for r in self._internal_value.values()
                    if self._postfilter(r)]
        return list(self._internal_value.values())


class GroupByFields(GroupBy):
    def __init__(self, _groupfields, **kwargs):
        self._groupfields = _groupfields

        def _grouping(obj):
            return tuple([(getattr(obj, f)) for f in _groupfields])
        kwargs.update({'_grouping': _grouping})
        super(GroupByFields, self).__init__(**kwargs)

    def _get_const_fields(self, key):
        return {k: key[n] for n, k in enumerate(self._groupfields)}

    def _get(self, **kwargs):
        return super(GroupByFields, self)._get(DataClass(**kwargs))
