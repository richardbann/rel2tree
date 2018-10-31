import copy


def _(x):
    return x


class Aggregator:
    def __init__(self, aggregator, _where=None, _sortkey=None):
        self._list = []
        self._where = _where
        self._sortkey = _sortkey
        self._aggregator = aggregator

    def feed(self, iterable):
        self._list.extend(iterable)
        return self

    def apply_clauses(self):
        lst = self._list
        if self._where:
            lst = [r for r in lst if self._where(r)]
            if self._sortkey:
                lst.sort(key=self._sortkey)
                return lst
            return lst
        if self._sortkey:
            return sorted(lst, key=self._sortkey)
        return lst

    def get(self, _groupkey=None):
        lst = self.apply_clauses()
        return self._aggregator(lst)


class Const:
    def __init__(self, value):
        self._value = value

    def feed(self, iterable):
        pass

    def get(self, _groupkey=None):
        return self._value


class GroupKey(Const):
    def __init__(self, transform):
        super().__init__(0)
        self.transform = transform

    def get(self, _groupkey=None):
            return self.transform(_groupkey)


class Dict(Aggregator):
    def __init__(self, _where=None, _sortkey=None, **kwargs):
        super().__init__(_, _where, _sortkey)
        self._fields = kwargs

    def get(self, _groupkey=None):
        lst = self.apply_clauses()

        for n, f in self._fields.items():
            f.feed(lst)

        return {n: f.get(_groupkey=_groupkey) for n, f in self._fields.items()}


class GroupBy(Aggregator):
    def __init__(
        self, aggregator, groupkey,
        _where=None, _sortkey=None, _having=None, _post_sortkey=None
    ):
        super().__init__(_, _where, _sortkey)
        self.aggregator = aggregator
        self.groupkey = groupkey
        self._having = _having
        self._post_sortkey = _post_sortkey

    def get(self, _groupkey=None):
        lst = self.apply_clauses()
        ret = {}
        for r in lst:
            key = self.groupkey(r)
            ret.setdefault(key, [])
            ret[key].append(r)

        ret = [
            copy.deepcopy(self.aggregator).feed(g).get(_groupkey=k)
            for k, g in ret.items()
        ]

        if self._having:
            ret = [r for r in ret if self._having(r)]
        if self._post_sortkey:
            ret.sort(key=self._post_sortkey)

        return ret
