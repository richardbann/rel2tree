import unittest
import json
import decimal

from rel2tree import rel2tree
from rel2tree import encoder


class SimpleTestCase(unittest.TestCase):

    # @unittest.skip('test')
    def test_aggregator_simple(self):
        a = rel2tree.Aggregator(
            _initial=0,
            _aggregator=lambda acc, item: acc + item
        )
        a._feed(1)._feed(2)._feed(3)
        self.assertEqual(a._value(), 6)

    # @unittest.skip('test')
    def test_aggregator_filter_even(self):
        a = rel2tree.Sum(
            _prefilter=lambda item: item % 2 == 0
        )
        a._feedmany([1, 2, 3])
        self.assertEqual(a._value(), 2)
        s = json.dumps(a, cls=encoder.JSONEncoder)
        s = json.loads(s)
        self.assertEqual(s, 2)

    # @unittest.skip('test')
    def test_simple_list(self):
        a = rel2tree.SimpleList(
            _prefilter=lambda x: x < 4,
        )
        a._feed(1)._feed(2)._feed(3)._feed(4)
        self.assertEqual(a._value(), [1, 2, 3])

    # @unittest.skip('test')
    def test_struct(self):
        a = rel2tree.Struct(
            numbers=rel2tree.List(
                num=rel2tree.ExtractField('num')
            ),
            sum=rel2tree.SumField('num'),
            max=rel2tree.Computed(
                lambda r: max([x.num._value() for x in r.numbers])
            ),
            something=rel2tree.Constant(2),
        )
        a._feedmany([
            {'num': 1},
            {'num': 2},
            {'num': 3},
            {'num': 4},
            {'num': 5}
        ])
        # print(json.dumps(a, cls=encoder.DecimalJSONEncoder, indent=2))
        s = json.dumps(a, cls=encoder.JSONEncoder)
        s = json.loads(s)
        self.assertEqual(s, {
            'max': 5,
            'sum': 15,
            'numbers': [
                {'num': 1},
                {'num': 2},
                {'num': 3},
                {'num': 4},
                {'num': 5}],
            'something': 2
        })

    # @unittest.skip('test')
    def test_groupby(self):
        a = rel2tree.GroupBy(
            _grouping=lambda obj: obj['client_id'],
            sumorders=rel2tree.SumField('quantity'),
        )
        a._feed({'client_id': 1, 'quantity': 10})
        a._feed({'client_id': 1, 'quantity': 20})
        a._feed({'client_id': 2, 'quantity': 100})
        s = json.dumps(a, cls=encoder.JSONEncoder)
        s = json.loads(s)
        self.assertEqual(s, [
            {'groupKey': 1, 'sumorders': 30},
            {'groupKey': 2, 'sumorders': 100},
        ])

    # @unittest.skip('test')
    def test_groupbyfields(self):
        a = rel2tree.GroupByFields(
            client_id=rel2tree.GroupingField(),
            sumorders=rel2tree.SumField('quantity'),
        )
        a._feed({'client_id': 1, 'quantity': 10})
        a._feed({'client_id': 1, 'quantity': 20})
        a._feed({'client_id': 2, 'quantity': 100})
        s = json.dumps(a, cls=encoder.JSONEncoder)
        s = json.loads(s)
        self.assertEqual(s, [
            {'client_id': 1, 'sumorders': 30},
            {'client_id': 2, 'sumorders': 100}
        ])

    # @unittest.skip('test')
    def test_complex(self):
        def include_client(client):
            return len(client.free) + len(client.credit)

        def get_currencies(client):
            return list(set([f.currencyID._value() for f in client.free] +
                            [c.currencyID._value() for c in client.credit]))

        def balanceitem(o):
            return 'free' in o or 'credit' in o

        a = rel2tree.Struct(
            _prefilter=lambda x: x['clientID'] != 444,
            balances=rel2tree.GroupByFields(
                _prefilter=balanceitem,
                _postfilter=include_client,
                clientID=rel2tree.GroupingField(),
                free=rel2tree.GroupByFields(
                    _prefilter=lambda o: 'free' in o,
                    _postfilter=lambda x: x.amount,
                    currencyID=rel2tree.GroupingField(),
                    amount=rel2tree.SumField('free'),
                ),
                credit=rel2tree.GroupByFields(
                    _prefilter=lambda o: 'credit' in o,
                    _postfilter=lambda x: x.amount,
                    currencyID=rel2tree.GroupingField(),
                    amount=rel2tree.SumField('credit'),
                ),
                currencies=rel2tree.Computed(get_currencies),
            ),
            clientDetails=rel2tree.GroupByFields(
                _prefilter=lambda o: 'clientCode' in o,
                clientID=rel2tree.GroupingField(),
                clientCode=rel2tree.GroupingField(),
            )
        )

        a._feed({'clientID': 111, 'currencyID': 'EUR', 'free': 123})
        a._feed({'clientID': 111, 'currencyID': 'EUR', 'credit': 50})
        a._feed({'clientID': 111, 'currencyID': 'PLN', 'free': 20})
        a._feed({'clientID': 111, 'currencyID': 'EUR', 'free': 2})
        a._feed({'clientID': 111, 'currencyID': 'PLN', 'free': -18})
        a._feed({'clientID': 222, 'currencyID': 'EUR', 'free': 123})
        a._feed({'clientID': 111, 'currencyID': 'PLN', 'free': -2})
        a._feed({'clientID': 222, 'currencyID': 'EUR', 'free': -123})
        a._feed({'clientID': 333, 'currencyID': 'EUR', 'free': 123})
        a._feed({'clientID': 333, 'currencyID': 'GBP', 'free': 200})
        a._feed({'clientID': 444, 'currencyID': 'EUR', 'free': 2000})

        a._feed({'clientID': 222, 'clientCode': '00222'})
        a._feed({'clientID': 111, 'clientCode': '00111'})
        # print(json.dumps(a, cls=encoder.JSONEncoder, indent=2))

        self.assertEqual(len(a._value()), 2)
        b = a.balances
        self.assertEqual(len(b._value()), 2)
        self.assertEqual(len(b._get({'clientID': 111})._value()), 4)
        self.assertEqual(len(b._get({'clientID': 111}).currencies._value()), 1)
        self.assertEqual(len(b._get({'clientID': 333}).currencies._value()), 2)

    # @unittest.skip('test')
    def test_field_ordering(self):
        a = rel2tree.Struct(
            a=rel2tree.Constant(1),
            b=rel2tree.Constant(2),
            c=rel2tree.Constant(3),
            d=rel2tree.Struct(
                d1=rel2tree.Constant('d1'),
                d2=rel2tree.Constant('d2'),
            ),
            a_plus_b=rel2tree.Computed(lambda x: x.a._value() + x.b._value()),
            g=rel2tree.GroupByFields(
                x=rel2tree.GroupingField(),
                y=rel2tree.GroupingField(),
                sum=rel2tree.SumField('q')
            )
        )

        a._feed({'x': 1, 'y': 1, 'q': 10})
        a._feed({'x': 1, 'y': 2, 'q': 10})
        a._feed({'x': 1, 'y': 1, 'q': 3})
        s = json.dumps(a, cls=encoder.JSONEncoder)
        self.assertEqual(
            s,
            ('{"a": 1, "b": 2, "c": 3, "d": {"d1": "d1", "d2": "d2"},'
             ' "a_plus_b": 3, "g": ['
             '{"x": 1, "y": 1, "sum": 13}, '
             '{"x": 1, "y": 2, "sum": 10}]}')
        )


@unittest.skip('only for performance measuring')
class LongTest(unittest.TestCase):
    def test_many(self):
        def include_client(client):
            return len(client.free) + len(client.credit)

        def get_currencies(client):
            return list(set([f.currencyID._value() for f in client.free] +
                            [c.currencyID._value() for c in client.credit]))

        a = rel2tree.Struct(
            type=rel2tree.Constant('BALANCE'),
            balance=rel2tree.Struct(
                _prefilter=lambda d: d['clientID'] != 444,
                clients=rel2tree.GroupByFields(
                    _postfilter=include_client,
                    clientID=rel2tree.GroupingField(),
                    free=rel2tree.GroupByFields(
                        _prefilter=lambda obj: 'free' in obj,
                        _postfilter=lambda x: x.amount,
                        currencyID=rel2tree.GroupingField(),
                        amount=rel2tree.SumField('free'),
                    ),
                    credit=rel2tree.GroupByFields(
                        _prefilter=lambda obj: 'credit' in obj,
                        _postfilter=lambda x: x.amount,
                        currencyID=rel2tree.GroupingField(),
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
            free = decimal.Decimal(random.randint(100, 1000))
            credit = decimal.Decimal(random.randint(100, 1000))
            a._feed({
                'clientID': clientID,
                'currencyID': currencyID,
                'free': free,
                'credit': credit,
            })
            i += 1
        print(json.dumps(a, cls=encoder.DecimalJSONEncoder, indent=2))
