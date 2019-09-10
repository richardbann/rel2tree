__all__ = ["f", ]


class L(list):
    """Slight modification of list so it can keep the groupkey."""

    def __init__(self, l, gk):
        self.gk = gk
        super().__init__(l)


class T:
    """Termination value, not chainable.

    Should not be used by end-users unless they want to extend
    F objects.
    """

    def __init__(self, fnc=lambda x: x, parent=None):
        self.fnc = fnc
        self.parent = parent

    def __call__(self, lst):
        if self.parent:
            lst = self.parent(lst)
        return self.fnc(lst)

    def groupkey(self, level=0):
        """Use it to access the group key deep inside a groupby.

        In case of nested groupby's, groupkey(0) is the deepest level group key,
        groupkey(1) is the one on the next level up.
        """

        def _(lst):
            try:
                return lst.gk[level]
            except (AttributeError, IndexError):
                return None

        return T(fnc=_)


class F(T):
    """Chainable `manipulator` of (mainly) lists."""

    def t(self, fnc):
        return T(fnc=fnc, parent=self)

    def f(self, fnc):
        return F(fnc=fnc, parent=self)

    def map(self, fnc):
        return self.f(lambda x: list(map(fnc, x)))

    def filter(self, fnc):
        return self.f(lambda x: list(filter(fnc, x)))

    def sort(self, fnc=lambda x: x):
        return self.f(lambda x: sorted(x, key=fnc))

    def dict(self, d):
        return self.t(
            lambda x: dict((k, v(x) if isinstance(v, T) else v) for k, v in d.items())
        )

    def groupby(self, fnc, f=None, groupkey=True):
        if not f:
            f = F()

        def _(lst):
            gb = {}
            for item in lst:
                gk = fnc(item)
                if not groupkey:
                    default = []
                elif isinstance(lst, L):
                    default = L([], [gk] + lst.gk)
                else:
                    default = L([], [gk])
                bucket = gb.setdefault(gk, default)
                bucket.append(item)
            return gb.values()

        return self.f(lambda x: [f(b) for b in _(x)])

    def distinct(self, fnc=lambda x: x):
        return self.groupby(fnc, groupkey=False).map(lambda x: x[0])


f = F()
