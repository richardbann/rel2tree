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
            something=rel2tree.Constant(2),
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
            sumorders=rel2tree.Aggregator(
                0, lambda v, obj: v + obj.quantity),
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
            sumorders=rel2tree.Aggregator(
                0, lambda v, obj: v + obj.quantity),
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

    def test_complex(self):
        def include_client(client):
            return len(client.free._value()) + len(client.credit._value())

        def get_currencies(client):
            free = client.free._value()
            credit = client.credit._value()
            return list(set([f.currencyID._value() for f in free] +
                            [c.currencyID._value() for c in credit]))

        a = rel2tree.Struct(
            type=rel2tree.Constant('BALANCE'),
            balance=rel2tree.Struct(
                _prefilter=lambda x: x.clientID != 444,
                clients=rel2tree.GroupByFields(
                    ('clientID',),
                    _postfilter=include_client,
                    free=rel2tree.GroupByFields(
                        ('currencyID',),
                        _prefilter=lambda obj: hasattr(obj, 'free'),
                        _postfilter=lambda x: x.amount._value(),
                        amount=rel2tree.SumField('free'),
                    ),
                    credit=rel2tree.GroupByFields(
                        ('currencyID',),
                        _prefilter=lambda obj: hasattr(obj, 'credit'),
                        _postfilter=lambda x: x.amount._value(),
                        amount=rel2tree.SumField('credit'),
                    ),
                    currencies=rel2tree.Computed(get_currencies),
                ),
            ),
        )

        a._feed(clientID=111, currencyID='EUR', free=123)
        a._feed(clientID=111, currencyID='EUR', credit=50)
        a._feed(clientID=111, currencyID='PLN', free=20)
        a._feed(clientID=111, currencyID='EUR', free=2)
        a._feed(clientID=111, currencyID='PLN', free=-18)
        a._feed(clientID=222, currencyID='EUR', free=123)
        a._feed(clientID=111, currencyID='PLN', free=-2)
        a._feed(clientID=222, currencyID='EUR', free=-123)
        a._feed(clientID=333, currencyID='EUR', free=123)
        a._feed(clientID=333, currencyID='GBP', free=200)
        a._feed(clientID=444, currencyID='EUR', free=2000)
        print(json.dumps(a, cls=encoder.JSONEncoder, indent=2))

        self.assertEqual(len(a), 2)
        cli = a.balance.clients
        self.assertEqual(len(cli), 2)
        self.assertEqual(len(cli._get(clientID=111)), 4)
        self.assertEqual(len(cli._get(clientID=111).currencies), 1)
        self.assertEqual(len(cli._get(clientID=333).currencies), 2)

    def test_field_ordering(self):
        a = rel2tree.Struct(
            a=rel2tree.Constant(1),
            b=rel2tree.Constant(2),
            c=rel2tree.Constant(3),
            d=rel2tree.Struct(
                d1=rel2tree.Constant('d1'),
                d2=rel2tree.Constant('d2'),
            ),
            calc=rel2tree.Computed(lambda x: x.a._value() + x.b._value()),
            g=rel2tree.GroupByFields(
                ('x', 'y'),
                sum=rel2tree.SumField('q')
            )
        )

        a._feed(x=1, y=1, q=10)
        a._feed(x=1, y=2, q=10)
        a._feed(x=1, y=1, q=3)
        print(json.dumps(a, cls=encoder.JSONEncoder, indent=2))


@unittest.skip('only for performance measuring')
class LongTest(unittest.TestCase):
    def test_many(self):
        def include_client(client):
            return len(client.free._value()) + len(client.credit._value())

        def get_currencies(client):
            free = client.free._value()
            credit = client.credit._value()
            return list(set([f.currencyID._value() for f in free] +
                            [c.currencyID._value() for c in credit]))

        a = rel2tree.Struct(
            type=rel2tree.Constant('BALANCE'),
            balance=rel2tree.Struct(
                _prefilter=lambda x: x.clientID != 444,
                clients=rel2tree.GroupByFields(
                    ('clientID',),
                    _postfilter=include_client,
                    free=rel2tree.GroupByFields(
                        ('currencyID',),
                        _prefilter=lambda obj: hasattr(obj, 'free'),
                        _postfilter=lambda x: x.amount._value(),
                        amount=rel2tree.SumField('free'),
                    ),
                    credit=rel2tree.GroupByFields(
                        ('currencyID',),
                        _prefilter=lambda obj: hasattr(obj, 'credit'),
                        _postfilter=lambda x: x.amount._value(),
                        amount=rel2tree.SumField('credit'),
                    ),
                    currencies=rel2tree.Computed(get_currencies),
                ),
            ),
        )

        import random
        clients = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        currencies = ['EUR', 'PLN', 'RON']
        i = 0
        while i < 50000:
            clientID = random.choice(clients)
            currencyID = random.choice(currencies)
            free = random.randint(100, 1000)
            credit = random.randint(100, 1000)
            a._feed(
                clientID=clientID,
                currencyID=currencyID,
                free=free,
                credit=credit,
            )
            i += 1
        print(json.dumps(a, cls=encoder.JSONEncoder, indent=2))
