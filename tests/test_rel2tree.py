import unittest
# from datetime import date

from rel2tree.core import Aggregator, Map, Dict, GroupBy
from rel2tree.utils import const, Const, field, FirstField
from rel2tree.utils import MinField, MaxField, SumField, AvgField
from rel2tree.utils import GroupByFields


def identity(x):
    return x


def neg(x):
    return -x


def even(x):
    return x % 2 == 0


def first(x):
    if len(x):
        return x[0]
    return None


class AggregatorTestCase(unittest.TestCase):
    def test_simple(self):
        a = Aggregator(identity)
        self.assertEqual(a.get([1, 2, 3]), [1, 2, 3])

    def test_clause(self):
        a = Aggregator(sum, _where=even)
        self.assertEqual(a.get([1, 2, 3, 4]), 6)

    def test_filter_sort(self):
        a = Aggregator(first, _where=even, _sortkey=neg)
        self.assertEqual(a.get([1, 2, 3, 4, 5]), 4)

    def test_sort_only(self):
        a = Aggregator(first, _sortkey=neg)
        self.assertEqual(a.get([1, 2, 3]), 3)


class MapTestCase(unittest.TestCase):
    def test_map(self):
        a = Map(const(4))
        self.assertEqual(a.get([1, 2, 3]), [4,  4, 4])


class DictTestCase(unittest.TestCase):
    def test_dict(self):
        lst = [1, 2, 3]
        a = Dict(
            const=Aggregator(const(3))
        )
        self.assertEqual(a.get(lst), {'const': 3})

        b = Dict(
            items=Aggregator(identity),
            sum=Aggregator(sum)
        )
        self.assertEqual(b.get(lst), {'items': [1, 2, 3], 'sum': 6})


class GroupByTestCase(unittest.TestCase):
    def test_groupby(self):
        a = Dict(
            report=Const('X001'),
            groups=GroupBy(
                field('g'),
                Dict(
                    key=FirstField('g'),
                    values=Map(field('v')),
                    sum=SumField('v')
                ),
                _sortkey=field('v'),
                _post_sortkey=field('key'),
                _having=lambda x: x['key'] in ('a', 'b')
            )
        )

        self.assertEqual(
            a.get([
                {'g': 'a', 'v': 3},
                {'g': 'c', 'v': 2},
                {'g': 'a', 'v': 1},
                {'g': 'b', 'v': 4},
                {'g': 'c', 'v': 5},
            ]),
            {
                'report': 'X001',
                'groups': [
                    {'key': 'a', 'values': [1, 3], 'sum': 4},
                    {'key': 'b', 'values': [4], 'sum': 4}
                ]
            }
        )

    def test_groupby_no_clause(self):
        a = Dict(
            report=Const('X002'),
            groups=GroupBy(
                field('g'),
                Dict(
                    key=FirstField('g'),
                    values=Map(field('v'), _sortkey=field('v')),
                    sum=SumField('v')
                ),
            )
        )
        self.assertEqual(
            a.get([
                {'g': 'a', 'v': 3},
                {'g': 'c', 'v': 2},
                {'g': 'a', 'v': 1},
                {'g': 'b', 'v': 4},
                {'g': 'c', 'v': 5},
            ]),
            {
                'report': 'X002',
                'groups': [
                    {'key': 'a', 'values': [1, 3], 'sum': 4},
                    {'key': 'c', 'values': [2, 5], 'sum': 7},
                    {'key': 'b', 'values': [4], 'sum': 4}
                ]
            }
        )


class FieldsTestCase(unittest.TestCase):
    def test_min_max_sum(self):
        a = Dict(
            all=Aggregator(identity),
            min=MinField('a'),
            max=MaxField('a'),
            sum=SumField('a'),
            avg=AvgField('a')
        )
        self.assertEqual(
            a.get([
                {'a': 1},
                {'a': 2},
                {'a': 3},
                {'a': 4},
                {'a': 5},
                {'a': 6},
            ]),
            {
                'all': [
                    {'a': 1}, {'a': 2}, {'a': 3},
                    {'a': 4}, {'a': 5}, {'a': 6}
                ],
                'min': 1,
                'max': 6,
                'sum': 21,
                'avg': 3.5
            }
        )

    def test_groub_by_fields(self):
        a = GroupByFields(['a', 'b'], Dict(
                a=FirstField('a'),
                b=FirstField('b'),
                c=SumField('c')
        ))
        self.assertEqual(
            a.get([
                {'a': 1, 'b': 1, 'c': 1},
                {'a': 1, 'b': 1, 'c': 2},
                {'a': 1, 'b': 2, 'c': 3},
                {'a': 1, 'b': 2, 'c': 4},
                {'a': 1, 'b': 2, 'c': 5},
                {'a': 2, 'b': 1, 'c': 6},
                {'a': 2, 'b': 2, 'c': 7},
                {'a': 2, 'b': 3, 'c': 8},
                {'a': 2, 'b': 3, 'c': 9},
                {'a': 3, 'b': 1, 'c': 10},
                {'a': 3, 'b': 1, 'c': 11},
            ]), [
                {'a': 1, 'b': 1, 'c': 3},
                {'a': 1, 'b': 2, 'c': 12},
                {'a': 2, 'b': 1, 'c': 6},
                {'a': 2, 'b': 2, 'c': 7},
                {'a': 2, 'b': 3, 'c': 17},
                {'a': 3, 'b': 1, 'c': 21}
            ]
        )
