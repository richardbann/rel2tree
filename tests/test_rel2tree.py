import unittest
from datetime import date

from rel2tree.core import Aggregator, Dict, GroupBy, GroupKey, Const, _
from rel2tree.fields import (
    MinField, MaxField, SumField, List, GroupByFields,
    GroupKeyField, AvgField, ListFields
)


def neg(x):
    return -x


def even(x):
    return x % 2 == 0


def first(x):
    if len(x):
        return x[0]
    return None


def const(x):
    def _inner(i):
        return x
    return _inner


class AggregatorTestCase(unittest.TestCase):
    def test_aggregator(self):
        a = Aggregator(_)
        a.feed([1, 2, 3])
        self.assertEqual(a.get(), [1, 2, 3])

    def test_aggregator_clause(self):
        a = Aggregator(sum, _where=even)
        a.feed([1, 2, 3, 4])
        self.assertEqual(a.get(), 6)

    def test_aggregator_sort(self):
        a = Aggregator(first, _where=even, _sortkey=neg)
        a.feed([1, 2, 3, 4])
        self.assertEqual(a.get(), 4)

    def test_aggregator_sort_only(self):
        a = Aggregator(first, _sortkey=neg)
        a.feed([1, 2, 3])
        self.assertEqual(a.get(), 3)
        a.feed([4, 5])
        self.assertEqual(a.get(), 5)
        a.feed([0])
        self.assertEqual(a.get(), 5)


class DictTestCase(unittest.TestCase):
    def test_dict(self):
        a = Dict(
            const=Aggregator(const(3))
        )
        a.feed([1, 2, 3])
        self.assertEqual(a.get(), {'const': 3})

        b = Dict(
            items=Aggregator(_),
            sum=Aggregator(sum)
        )
        b.feed([1, 2, 3])
        self.assertEqual(b.get(), {'items': [1, 2, 3], 'sum': 6})


class GroupByTestCase(unittest.TestCase):
    def test_groupby(self):
        a = Dict(
            report=Const('X001'),
            groups=GroupBy(
                Dict(
                    key=GroupKey(_),
                    values=Aggregator(lambda x: [v['v'] for v in x]),
                    sum=Aggregator(lambda x: sum([v['v'] for v in x]))
                ),
                lambda x: x['g'],
                _sortkey=lambda x: x['v'],
                _post_sortkey=lambda x: x['key'],
                _having=lambda x: x['key'] in ('a', 'b')
            )
        )
        a.feed([
            {'g': 'a', 'v': 3},
            {'g': 'c', 'v': 2},
            {'g': 'a', 'v': 1},
            {'g': 'b', 'v': 4},
            {'g': 'c', 'v': 5},
        ])
        self.assertEqual(
            a.get(),
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
            report=Const('X001'),
            groups=GroupBy(
                Dict(
                    key=GroupKey(_),
                    values=Aggregator(
                        lambda x: [v['v'] for v in x],
                        _sortkey=lambda x: x['v']
                    ),
                    sum=Aggregator(lambda x: sum([v['v'] for v in x]))
                ),
                lambda x: x['g'],
            )
        )
        a.feed([
            {'g': 'a', 'v': 3},
            {'g': 'c', 'v': 2},
            {'g': 'a', 'v': 1},
            {'g': 'b', 'v': 4},
            {'g': 'c', 'v': 5},
        ])
        self.assertEqual(
            a.get(),
            {
                'report': 'X001',
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
            all=Aggregator(_),
            min=MinField('a'),
            max=MaxField('a'),
            sum=SumField('a')
        )
        a.feed([
            {'a': 1},
            {'a': 2},
            {'a': 3},
            {'a': 4},
            {'a': 5},
            {'a': 6},
        ])
        self.assertEqual(
            a.get(), {
                'all': [
                    {'a': 1}, {'a': 2}, {'a': 3},
                    {'a': 4}, {'a': 5}, {'a': 6}
                ],
                'min': 1,
                'max': 6,
                'sum': 21
            }
        )

    def test_transform(self):
        a = List(
            lambda x: {
                'first': x['fn'],
                'last': x['ln'],
                'full': x['fn'] + ' ' + x['ln']
            }
        )
        a.feed([
            {'fn': 'John', 'ln': 'Doe'},
            {'fn': 'Eve', 'ln': 'Smith'},
        ])
        self.assertEqual(
            a.get(), [
                {'first': 'John', 'last': 'Doe', 'full': 'John Doe'},
                {'first': 'Eve', 'last': 'Smith', 'full': 'Eve Smith'}
            ]
        )

    def test_groub_by_fields(self):
        a = GroupByFields(['a', 'b'], Dict(
            a=GroupKeyField('a'),
            b=GroupKeyField('b'),
            c=SumField('c')
        ))
        a.feed([
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
        ])
        self.assertEqual(
            a.get(), [
                {'a': 1, 'b': 1, 'c': 3},
                {'a': 1, 'b': 2, 'c': 12},
                {'a': 2, 'b': 1, 'c': 6},
                {'a': 2, 'b': 2, 'c': 7},
                {'a': 2, 'b': 3, 'c': 17},
                {'a': 3, 'b': 1, 'c': 21}
            ]
        )

    def test_real_example(self):
        min, max = date(2018, 10, 2), date(2018, 10, 4)
        a = GroupByFields(['name'], Dict(
            name=GroupKeyField('name'),
            avg=AvgField('price'),
            prices=ListFields([
                'date',
                'price'
            ])
        ),
            _where=lambda x: (
                (not min or x['date'] >= min) and
                (not max or x['date'] <= max)
            )
        )

        a.feed([
            {'name': 'A', 'date': date(2018, 10, 1), 'price': 1},
            {'name': 'A', 'date': date(2018, 10, 2), 'price': 2},
            {'name': 'A', 'date': date(2018, 10, 3), 'price': 3},
            {'name': 'B', 'date': date(2018, 10, 1), 'price': 4},
            {'name': 'B', 'date': date(2018, 10, 2), 'price': 5},
            {'name': 'B', 'date': date(2018, 10, 3), 'price': 6},
            {'name': 'B', 'date': date(2018, 10, 4), 'price': 7},
        ])
        self.assertEqual(
            a.get(), [
                {
                    'name': 'A',
                    'avg': 2.5,
                    'prices': [
                        {'date': date(2018, 10, 2), 'price': 2},
                        {'date': date(2018, 10, 3), 'price': 3}
                    ]
                },
                {
                    'name': 'B',
                    'avg': 6.0,
                    'prices': [
                        {'date': date(2018, 10, 2), 'price': 5},
                        {'date': date(2018, 10, 3), 'price': 6},
                        {'date': date(2018, 10, 4), 'price': 7}
                    ]
                }
            ]
        )
