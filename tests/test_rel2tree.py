import unittest
import json
import decimal

from rel2tree import (
    Aggregator, Sum, SimpleList, ExtractField, SumField,
    GroupByFields, GroupingField, List,
    Struct, Computed, Constant, GroupBy,
    JSONEncoder, DecimalJSONEncoder,
)


class SimpleTestCase(unittest.TestCase):

    # @unittest.skip('test')
    def test_aggregator_simple(self):
        a = Aggregator(
            _initial=0,
            _aggregator=lambda acc, item: acc + item
        )
        a._feed(1)._feed(2)._feed(3)
        self.assertEqual(a._value(), 6)

    # @unittest.skip('test')
    def test_aggregator_filter_even(self):
        a = Sum(
            _prefilter=lambda item: item % 2 == 0
        )
        a._feedmany([1, 2, 3])
        self.assertEqual(a._value(), 2)
        s = json.dumps(a, cls=JSONEncoder)
        s = json.loads(s)
        self.assertEqual(s, 2)

    # @unittest.skip('test')
    def test_simple_list(self):
        a = SimpleList(
            _prefilter=lambda x: x < 4,
            _sortkey=lambda o: -o,
        )
        a._feed(1)._feed(2)._feed(3)._feed(4)
        # print(json.dumps(a, cls=DecimalJSONEncoder, indent=2))
        self.assertEqual(a._value(), [3, 2, 1])

    # @unittest.skip('test')
    def test_struct(self):
        a = Struct(
            numbers=List(
                _sortkey=lambda o: -o.num._value(),
                num=ExtractField('num')
            ),
            sum=SumField('num'),
            max=Computed(
                lambda r: max([x.num._value() for x in r.numbers])
            ),
            something=Constant(2),
        )
        a._feedmany([
            {'num': 1},
            {'num': 2},
            {'num': 3},
            {'num': 4},
            {'num': 5}
        ])
        # print(json.dumps(a, cls=DecimalJSONEncoder, indent=2))
        s = json.dumps(a, cls=JSONEncoder)
        s = json.loads(s)
        self.assertEqual(s, {
            'max': 5,
            'sum': 15,
            'numbers': [
                {'num': 5},
                {'num': 4},
                {'num': 3},
                {'num': 2},
                {'num': 1}],
            'something': 2
        })

    # @unittest.skip('test')
    def test_groupby(self):
        a = GroupBy(
            _grouping=lambda obj: obj['client_id'],
            sumorders=SumField('quantity'),
        )
        a._feed({'client_id': 1, 'quantity': 10})
        a._feed({'client_id': 1, 'quantity': 20})
        a._feed({'client_id': 2, 'quantity': 100})
        s = json.dumps(a, cls=JSONEncoder)
        s = json.loads(s)
        self.assertEqual(s, [
            {'groupKey': 1, 'sumorders': 30},
            {'groupKey': 2, 'sumorders': 100},
        ])

    # @unittest.skip('test')
    def test_groupbyfields(self):
        a = GroupByFields(
            client_id=GroupingField(),
            sumorders=SumField('quantity'),
        )
        a._feed({'client_id': 1, 'quantity': 10})
        a._feed({'client_id': 1, 'quantity': 20})
        a._feed({'client_id': 2, 'quantity': 100})
        s = json.dumps(a, cls=JSONEncoder)
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

        a = Struct(
            _prefilter=lambda x: x['clientID'] != 444,
            balances=GroupByFields(
                _prefilter=balanceitem,
                _postfilter=include_client,
                clientID=GroupingField(),
                free=GroupByFields(
                    _prefilter=lambda o: 'free' in o,
                    _postfilter=lambda x: x.amount,
                    currencyID=GroupingField(),
                    amount=SumField('free'),
                ),
                credit=GroupByFields(
                    _prefilter=lambda o: 'credit' in o,
                    _postfilter=lambda x: x.amount,
                    currencyID=GroupingField(),
                    amount=SumField('credit'),
                ),
                currencies=Computed(get_currencies),
            ),
            clientDetails=GroupByFields(
                _prefilter=lambda o: 'clientCode' in o,
                _sortkey=lambda o: o.clientCode._value(),
                clientID=GroupingField(),
                clientCode=GroupingField(),
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
        # print(json.dumps(a, cls=JSONEncoder, indent=2))

        self.assertEqual(len(a._value()), 2)
        b = a.balances
        self.assertEqual(len(b._value()), 2)
        self.assertEqual(len(b._get({'clientID': 111})._value()), 4)
        self.assertEqual(len(b._get({'clientID': 111}).currencies._value()), 1)
        self.assertEqual(len(b._get({'clientID': 333}).currencies._value()), 2)

    # @unittest.skip('test')
    def test_field_ordering(self):
        a = Struct(
            a=Constant(1),
            b=Constant(2),
            c=Constant(3),
            d=Struct(
                d1=Constant('d1'),
                d2=Constant('d2'),
            ),
            a_plus_b=Computed(lambda x: x.a._value() + x.b._value()),
            g=GroupByFields(
                x=GroupingField(),
                y=GroupingField(),
                sum=SumField('q')
            )
        )

        a._feed({'x': 1, 'y': 1, 'q': 10})
        a._feed({'x': 1, 'y': 2, 'q': 10})
        a._feed({'x': 1, 'y': 1, 'q': 3})
        s = json.dumps(a, cls=JSONEncoder)
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

        a = Struct(
            type=Constant('BALANCE'),
            balance=Struct(
                _prefilter=lambda d: d['clientID'] != 444,
                clients=GroupByFields(
                    _postfilter=include_client,
                    _sortkey=lambda o: o.clientID._value(),
                    clientID=GroupingField(),
                    free=GroupByFields(
                        _prefilter=lambda obj: 'free' in obj,
                        _postfilter=lambda x: x.amount,
                        _sortkey=lambda o: o.currencyID._value(),
                        currencyID=GroupingField(),
                        amount=SumField('free'),
                    ),
                    credit=GroupByFields(
                        _prefilter=lambda obj: 'credit' in obj,
                        _postfilter=lambda x: x.amount,
                        _sortkey=lambda o: o.currencyID._value(),
                        currencyID=GroupingField(),
                        amount=SumField('credit'),
                    ),
                    currencies=Computed(get_currencies, _sortkey=lambda o: o),
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
            # free = decimal.Decimal(random.randint(100, 1000))
            # credit = decimal.Decimal(random.randint(100, 1000))
            free = random.randint(100, 1000)
            credit = random.randint(100, 1000)

            a._feed({
                'clientID': clientID,
                'currencyID': currencyID,
                'free': free,
                'credit': credit,
            })
            i += 1
        print(json.dumps(a, cls=DecimalJSONEncoder, indent=2))
