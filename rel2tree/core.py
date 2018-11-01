import copy


def identity(x):
    return x


def const(c):
    def fnc(*args):
        return c
    return fnc


class Convert:
    def __init__(self, fnc, _where=const(True), _sortkey=const(0)):
        self._where = _where
        self._sortkey = _sortkey
        self.fnc = fnc

    def _get(self, iterable, groupkey):
        return self.fnc(iterable)

    def get(self, iterable, groupkey=None):
        iterable = [r for r in iterable if self._where(r)]
        iterable.sort(key=self._sortkey)
        return self._get(iterable, groupkey)


class Map(Convert):
    def _get(self, iterable, groupkey):
        return [self.fnc(x) for x in iterable]


class GroupKey(Convert):
    def get(self, iterable, groupkey=None):
        return self.fnc(groupkey)


class Dict(Convert):
    def __init__(self, _where=const(True), _sortkey=const(0), **kwargs):
        super().__init__(identity, _where, _sortkey)
        self.fields = kwargs

    def _get(self, iterable, groupkey):
        return {n: f.get(iterable, groupkey) for n, f in self.fields.items()}


class DictList(Dict):
    def _get(self, iterable, groupkey):
        return [{n: f(x) for n, f in self.fields.items()} for x in iterable]


class GroupBy(Convert):
    def __init__(
        self, groupkey, groupconvert,
        _where=const(True), _sortkey=const(0),
        _having=None, _post_sortkey=None
    ):
        super().__init__(identity, _where, _sortkey)
        self.groupconvert = groupconvert
        self.groupkey = groupkey
        self._having = _having
        self._post_sortkey = _post_sortkey

    def _get(self, iterable, groupkey):
        ret = {}
        for r in iterable:
            key = self.groupkey(r)
            ret.setdefault(key, [])
            ret[key].append(r)
        ret = [
            copy.deepcopy(self.groupconvert).get(g, k)
            for k, g in ret.items()
        ]
        if self._having:
            ret = [r for r in ret if self._having(r)]
        if self._post_sortkey:
            ret.sort(key=self._post_sortkey)
        return ret
