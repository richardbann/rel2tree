import copy


def id(x):
    return x


def const(x):
    return lambda a: x


class Field:
    def __init__(self, _where=None, _sortkey=None, _aggregator=id):
        if _where is not None:
            assert callable(_where), '_where must be callable'
        if _sortkey is not None:
            assert callable(_sortkey), '_sortkey must be callable'
        assert callable(_aggregator), '_aggregator must be callable'

        self._list = []
        self._where = _where
        self._sortkey = _sortkey
        self._aggregator = _aggregator

    def feed(self, iterable):
        self._list = iterable
        return self

    def applywhere(self):
        if self._where:
            self._list = [r for r in self._list if self._where(r)]

    def applysort(self):
        if self._sortkey:
            self._list.sort(key=self._sortkey)

    def get(self):
        self.applywhere()
        self.applysort()
        return self._aggregator([r for r in self._list])


class Computed:
    def __init__(self, fnc=id):
        assert callable(fnc), 'fnc must be callable'
        self._fnc = fnc

    def get(self, _dict):
        return self._fnc(_dict)


class Dict(Field):
    def __init__(self, _where=None, _sortkey=None, **kwargs):
        super().__init__(_where, _sortkey)
        for k, v in kwargs.items():
            if not isinstance(v, Field) and not isinstance(v, Computed):
                raise Exception('invalid field: %s' % k)
        self._fields = {
            k: v for k, v in kwargs.items() if isinstance(v, Field)
        }
        self._computed_fields = {
            k: v for k, v in kwargs.items() if isinstance(v, Computed)
        }

    def get(self):
        self.applywhere()
        self.applysort()
        for n, f in self._fields.items():
            try:
                f.feed(self._list)
            except Exception:
                print(n, f)

        ret = {n: f.get() for n, f in self._fields.items()}
        comp = {n: f.get(ret) for n, f in self._computed_fields.items()}
        ret.update(comp)
        return ret


class GroupBy(Field):
    def __init__(
        self, field=Field(), _groupkey=const(0),
        _where=None, _sortkey=None, _having=None, _post_sortkey=None
    ):
        super().__init__(_where, _sortkey)
        if _groupkey is not None:
            assert callable(_groupkey), '_groupkey must be callable'
        if _having is not None:
            assert callable(_having), '_having must be callable'
        if _post_sortkey is not None:
            assert callable(_post_sortkey), '_post_sortkey must be callable'
        assert isinstance(field, Field), 'invalid field in GroupBy'

        self.field = field
        self._groupkey = _groupkey or const(0)
        self._having = _having
        self._post_sortkey = _post_sortkey

    def get(self):
        self.applywhere()
        self.applysort()
        ret = {}
        for r in self._list:
            key = self._groupkey(r)
            ret.setdefault(key, [])
            ret[key].append(r)
        ret = [copy.copy(self.field).feed(g).get() for g in ret.values()]
        if self._having:
            ret = [r for r in ret if self._having(r)]
        if self._post_sortkey:
            ret.sort(key=self._post_sortkey)
        return ret
