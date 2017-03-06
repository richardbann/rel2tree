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

    def _json(self):
        return self._value()


class Aggregator(AggregatorBase):
    def __init__(self, initial, aggregator, _prefilter=None):
        self._internal_value = initial
        self._aggregator = aggregator
        self._prefilter = _prefilter


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
        for k, v in kwargs.items():
            if isinstance(v, AggregatorBase):
                self._aggregator_fields[k] = v
            elif isinstance(v, Computed):
                self._computed_fields[k] = v
            else:
                self._other_fields[k] = v
        self._internal_value = copy.deepcopy(self._aggregator_fields)

    def _aggregate(self, obj):
        for field_name in self._aggregator_fields:
            self._internal_value[field_name]._feedobject(obj)

    def __getattr__(self, field_name):
        if field_name in self._internal_value:
            return self._internal_value[field_name]
        msg = '%s object has no attribute %s'
        raise AttributeError(msg % (type(self).__name__, field_name))

    def _value(self):
        ret = self._internal_value
        computed = self._computed_fields.items()
        try:
            computed_values = {k: v._fnc(self) for k, v in computed}
        except Exception as e:
            raise ComputationError(e)
        ret.update(computed_values)
        ret.update(self._other_fields.items())
        return ret


class GroupBy(AggregatorBase):
    def __init__(self, **kwargs):
        self._grouping = kwargs.pop('_grouping', None)
        self._prefilter = kwargs.pop('_prefilter', None)
        self._fields = kwargs
        self._internal_value = OrderedDict()

    def _get_const_fields(self, key):
        return {'groupKey': key}

    def _aggregate(self, obj):
        key = self._grouping(obj)
        try:
            bucket = self._internal_value[key]
        except KeyError:
            kwargs = copy.deepcopy(self._fields)
            kwargs.update(self._get_const_fields(key))
            bucket = Struct(**kwargs)
            self._internal_value[key] = bucket
        bucket._feedobject(obj)

    def _get(self, key):
        return self._internal_value[key]

    def _value(self):
        return list(self._internal_value.values())


class GroupByFields(GroupBy):
    def __init__(self, _groupfields, **kwargs):
        self._groupkey_fields = _groupfields

        def _grouping(obj):
            return tuple([(getattr(obj, f)) for f in _groupfields])
        kwargs.update({'_grouping': _grouping})
        super(GroupByFields, self).__init__(**kwargs)

    def _get_const_fields(self, key):
        return {k: key[n] for n, k in enumerate(self._groupkey_fields)}
