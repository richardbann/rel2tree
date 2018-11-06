class Aggregator:
    def __init__(self, fnc, _where=None, _sortkey=None):
        self._where = _where
        self._sortkey = _sortkey
        self.fnc = fnc

    def _get(self, iterable):
        return self.fnc(iterable)

    def get(self, iterable):
        if self._where:
            iterable = [r for r in iterable if self._where(r)]
        else:
            iterable = iterable.copy()
        if self._sortkey:
            iterable.sort(key=self._sortkey)
        return self._get(iterable)


class Map(Aggregator):
    def _get(self, iterable):
        return [self.fnc(x) for x in iterable]


class Dict(Aggregator):
    def __init__(self, _where=None, _sortkey=None, **kwargs):
        super().__init__(None, _where, _sortkey)
        self.fields = kwargs

    def _get(self, iterable):
        return {k: v.get(iterable) for k, v in self.fields.items()}


class GroupBy(Aggregator):
    def __init__(
        self, groupkey, aggregator,
        _where=None, _sortkey=None,
        _having=None, _post_sortkey=None
    ):
        super().__init__(None, _where, _sortkey)
        self.aggregator = aggregator
        self.groupkey = groupkey
        self._having = _having
        self._post_sortkey = _post_sortkey

    def _get(self, iterable):
        ret = {}
        for r in iterable:
            key = self.groupkey(r)
            ret.setdefault(key, [])
            ret[key].append(r)
        ret = [self.aggregator.get(g) for g in ret.values()]
        if self._having:
            ret = [r for r in ret if self._having(r)]
        if self._post_sortkey:
            ret.sort(key=self._post_sortkey)
        return ret
