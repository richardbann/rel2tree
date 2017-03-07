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


class AggregatorBase(object):
    _internal_value = None
    _prefilter = None
    _creation_counter = 0

    @staticmethod
    def _aggregator(v, obj):
        pass  # pragma: no cover

    def __init__(self):
        self._creation_counter = AggregatorBase._creation_counter
        AggregatorBase._creation_counter += 1

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


class NoFeedMixin(object):
    def _feed(self, *args, **kwargs):
        pass

    def _feedobject(self, *args, **kwargs):
        pass

    def _feedmany(self, *args, **kwargs):
        pass


class Computed(NoFeedMixin, AggregatorBase):
    def __init__(self, fnc):
        self._fnc = fnc
        super(Computed, self).__init__()

    def _compute(self, parent):
        self._internal_value = self._fnc(parent)
        return self


class Constant(NoFeedMixin, AggregatorBase):
    def __init__(self, value):
        self._set_value(value)
        super(Constant, self).__init__()

    def _set_value(self, value):
        self._internal_value = value


class GroupingField(Constant):
    def __init__(self):
        super(GroupingField, self).__init__(None)


class Aggregator(AggregatorBase):
    def __init__(self, initial, aggregator, _prefilter=None):
        self._internal_value = initial
        self._aggregator = aggregator
        self._prefilter = _prefilter
        super(Aggregator, self).__init__()


class SumField(Aggregator):
    def __init__(self, field_name, _prefilter=None):
        def aggregator(v, obj):
            return v + getattr(obj, field_name)
        super(SumField, self).__init__(0, aggregator, _prefilter)


class List(AggregatorBase):
    def __init__(self, _prefilter=None):
        self._prefilter = _prefilter
        self._internal_value = []
        super(List, self).__init__()

    @staticmethod
    def _aggregator(v, obj):
        v.append(obj)
        return v


class Struct(AggregatorBase):
    def __init__(self, **kwargs):
        self._prefilter = kwargs.pop('_prefilter', None)
        self._aggregator_fields = {}
        self._computed_fields = {}
        for k, v in kwargs.items():
            if isinstance(v, Computed):
                self._computed_fields[k] = v
            elif isinstance(v, AggregatorBase):
                self._aggregator_fields[k] = v
            else:
                raise TypeError('invalid field type: %s: %s' % (k, v))
        self._internal_value = self._get_initial_value()
        fl = [(k, v) for k, v in kwargs.items()]
        fl = sorted(fl, key=lambda f: f[1]._creation_counter)
        self._all_fields = [k for k, v in fl]
        super(Struct, self).__init__()

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
                return self._computed_fields[field_name]._compute(self)
        msg = '%s object has no attribute %s'
        raise AttributeError(msg % (type(self).__name__, field_name))

    def _value(self):
        fl = [(field, getattr(self, field)) for field in self._all_fields]
        return OrderedDict(fl)


class GroupByBase(Struct):
    _postfilter = None
    _grouping = None

    def __init__(self, **kwargs):
        self._fields = kwargs
        super(GroupByBase, self).__init__(**kwargs)

    def _get_initial_value(self):
        return OrderedDict()  # preserve insertion order

    def _add_const_fields(self, kwargs, key):
        kwargs.update({'groupKey': Constant(key)})

    def _get_key(self, obj):
        return self._grouping(obj) if self._grouping else None

    def _aggregate(self, obj):
        key = self._get_key(obj)
        try:
            bucket = self._internal_value[key]
        except KeyError:
            kwargs = self._fields.copy()
            self._add_const_fields(kwargs, key)
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


class GroupBy(GroupByBase):
    def __init__(self, **kwargs):
        self._grouping = kwargs.pop('_grouping', None)
        self._postfilter = kwargs.pop('_postfilter', None)
        super(GroupBy, self).__init__(**kwargs)


class GroupByFields(GroupByBase):
    def _grouping(self, obj):
        return tuple([getattr(obj, k) for k in self._grouping_fields])

    def __init__(self, **kwargs):
        self._postfilter = kwargs.pop('_postfilter', None)
        self._grouping_fields = [k for k, v in kwargs.items()
                                 if isinstance(v, GroupingField)]
        super(GroupByFields, self).__init__(**kwargs)

    def _add_const_fields(self, kwargs, key):
        for i, field in enumerate(self._grouping_fields):
            kwargs[field]._set_value(key[i])

    def _get(self, **kwargs):
        return super(GroupByFields, self)._get(DataClass(**kwargs))
