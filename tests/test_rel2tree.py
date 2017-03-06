import unittest
import json

from rel2tree import rel2tree
from rel2tree import encoder


class SimpleTestCase(unittest.TestCase):
    def test_dataclass(self):
        dc = rel2tree.DataClass(a=12, b=42)
        s = json.dumps(dc, cls=encoder.JSONEncoder)
        s = json.loads(s)
        self.assertEqual(s, {"a": 12, "b": 42})

    def test_aggregator_simple(self):
        a = rel2tree.Aggregator(
            0,
            lambda v, obj: v + obj
        )
        a._feed(1)._feed(2)._feed(3)
        self.assertEqual(a._value(), 6)

    def test_aggregator_filter_even(self):
        a = rel2tree.Aggregator(
            0,
            lambda v, obj: v + obj,
            lambda obj: obj % 2 == 0)
        a._feedmany([1, 2, 3])
        self.assertEqual(a._value(), 2)
        s = json.dumps(a, cls=encoder.JSONEncoder)
        s = json.loads(s)
        self.assertEqual(s, 2)

    def test_list(self):
        a = rel2tree.List()
        a._feed(1)._feed(2)._feed(3)
        self.assertEqual(a._value(), [1, 2, 3])

    def test_struct(self):
        a = rel2tree.Struct(
            numbers=rel2tree.List(),
            sum=rel2tree.Aggregator(0, lambda v, obj: v + obj),
            max=rel2tree.Computed(
                lambda x: max(x.numbers._value())
            ),
            something=2,
        )
        a._feedmany([1, 2, 3, 4, 5])
        s = json.dumps(a, cls=encoder.JSONEncoder)
        s = json.loads(s)
        self.assertEqual(s, {
            "max": 5,
            "sum": 15,
            "numbers": [1, 2, 3, 4, 5],
            "something": 2
        })

    def test_groupby(self):
        a = rel2tree.GroupBy(
            _grouping=lambda obj: obj.client_id,
            sumorders=rel2tree.Aggregator(0, lambda v, obj: v + obj.quantity),
        )
        a._feed(client_id=1, quantity=10)
        a._feed(client_id=1, quantity=20)
        a._feed(client_id=2, quantity=100)
        s = json.dumps(a, cls=encoder.JSONEncoder)
        s = json.loads(s)
        self.assertEqual(s, [
            {"groupKey": 1, "sumorders": 30},
            {"groupKey": 2, "sumorders": 100},
        ])

    def test_groupbyfields(self):
        a = rel2tree.GroupByFields(
            _groupfields=('client_id',),
            sumorders=rel2tree.Aggregator(0, lambda v, obj: v + obj.quantity),
        )
        a._feed(client_id=1, quantity=10)
        a._feed(client_id=1, quantity=20)
        a._feed(client_id=2, quantity=100)
        s = json.dumps(a, cls=encoder.JSONEncoder)
        s = json.loads(s)
        self.assertEqual(s, [
            {"client_id": 1, "sumorders": 30},
            {"client_id": 2, "sumorders": 100}
        ])
