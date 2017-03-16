from collections import OrderedDict


class AggregatorBase(object):
    _creation_counter = 0

    def _aggregator(self, records, inner):
        return records

    def _ensure_attr(self, kwargs, attrname):
        if attrname in kwargs:
            setattr(self, attrname, kwargs.pop(attrname))
        elif not hasattr(self, attrname):
            setattr(self, attrname, None)

    def __init__(self, **kwargs):
        self._creation_counter = AggregatorBase._creation_counter
        AggregatorBase._creation_counter += 1
        self._ensure_attr(kwargs, '_aggregator')
        self._ensure_attr(kwargs, '_where')
        if kwargs:
            msg = ', '.join(['%s: %s' % (k, v) for k, v in kwargs.items()])
            msg = 'Invalid fields in Aggregator: %s' % msg
            raise TypeError(msg)
        self._all = []

    def _create(self, records, inner=False):
        if self._where:
            records = [r for r in records if self._where(r)]
        return self._aggregator(records, inner)


class HavingMixin(object):
    def __init__(self, **kwargs):
        self._ensure_attr(kwargs, '_having')
        super(HavingMixin, self).__init__(**kwargs)

    def _create(self, records, inner=False):
        records = super(HavingMixin, self)._create(records, inner)
        if not inner and self._having:
            return [r for r in records if self._having(r)]
        return records


class SortingMixin(object):
    def __init__(self, **kwargs):
        self._ensure_attr(kwargs, '_sortkey')
        super(SortingMixin, self).__init__(**kwargs)

    def _create(self, records, inner=False):
        records = super(SortingMixin, self)._create(records, inner)
        if not inner and self._sortkey:
            records.sort(key=self._sortkey)
        return records


class Constant(AggregatorBase):
    def __init__(self, value=None):
        self.value = value
        super(Constant, self).__init__()

    def _aggregator(self, records, inner):
        return self.value


class Computed(AggregatorBase):
    def __init__(self, fnc):
        self.fnc = fnc
        super(Computed, self).__init__()

    def _aggregator(self, records, inner):
        return None

    def _compute(self, parent):
        return self.fnc(parent)


class Struct(AggregatorBase):
    def __init__(self, **kwargs):
        self._fields = []
        for field_name in list(kwargs):
            val = kwargs[field_name]
            if isinstance(val, AggregatorBase):
                self._fields.append((field_name, val))
                kwargs.pop(field_name)
        self._fields.sort(key=lambda f: f[1]._creation_counter)
        super(Struct, self).__init__(**kwargs)

    def _aggregator(self, records, inner):
        ret = [(f, v._create(records)) for f, v in self._fields]
        ret = OrderedDict(ret)
        comp = [(f, v) for f, v in self._fields if isinstance(v, Computed)]
        for f, v in comp:
            ret[f] = v._compute(ret)
        return ret


class GroupBy(SortingMixin, HavingMixin, Struct):
    def __init__(self, **kwargs):
        self._ensure_attr(kwargs, '_grouping')
        super(GroupBy, self).__init__(**kwargs)

    def _aggregator(self, records, inner):
        if inner:
            return super(GroupBy, self)._aggregator(records, False)

        ret = OrderedDict()
        for r in records:
            key = self._grouping(r)
            if key not in ret:
                ret[key] = []
            ret[key].append(r)
        return [self._create(v, True) for v in ret.values()]
