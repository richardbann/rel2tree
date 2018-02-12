import unittest
import random
import decimal

# from rel2tree.utils import Sum, SumField, List, GroupByFields, GroupingField
from rel2tree.core import Field, Dict, Computed
from rel2tree.fields import Const, SumField, PickField, GroupByFields


def id(x):
    return x


def even(x):
    return x % 2 == 0


class SimpleTestCase(unittest.TestCase):
    # @unittest.skip('test')
    def test_field(self):
        f = Field(_aggregator=sum)
        f.feed([1, 2, 3])
        self.assertEqual(f.get(), 6)

    # @unittest.skip('test')
    def test_where(self):
        f = Field(_aggregator=sum, _where=even)
        f.feed([1, 2, 3])
        self.assertEqual(f.get(), 2)

    # @unittest.skip('test')
    def test_sort(self):
        f = Field(_aggregator=id, _sortkey=id)
        f.feed([2, 1, 3])
        self.assertEqual(f.get(), [1, 2, 3])

    # @unittest.skip('test')
    def test_empty(self):
        f = Field(_aggregator=sum)
        self.assertEqual(f.get(), 0)

    # @unittest.skip('test')
    def test_dict(self):
        f = Dict(
            c=Const('const'),
            s=Field(_aggregator=sum)
        )
        self.assertEqual(f.get(), {'c': 'const', 's': 0})

    # @unittest.skip('test')
    def test_computed(self):
        f = Dict(
            c=Const('const'),
            s=Field(_aggregator=sum),
            comp=Computed(lambda r: r['s'] * 2)
        )
        f.feed([1, 2, 3, 4])
        self.assertEqual(f.get(), {'c': 'const', 's': 10, 'comp': 20})

    # @unittest.skip('test')
    def test_groupby(self):
        f = GroupByFields('typ', field=Dict(
                typ=PickField('typ'),
                sum=SumField('n'),
            ))
        f.feed([
            {'typ': 'A', 'n': 1},
            {'typ': 'A', 'n': 2},
            {'typ': 'A', 'n': 3},
            {'typ': 'A', 'n': 4},
            {'typ': 'B', 'n': 5},
            {'typ': 'B', 'n': 6},
        ])
        self.assertEqual(f.get(), [
            {'typ': 'A', 'sum': 10}, {'typ': 'B', 'sum': 11}
        ])

    # @unittest.skip('test')
    def test_simple_dict(self):
        a = Dict(
            sum=SumField('num'),
            something=Const(2),
            maxinlist=Computed(
                lambda r: max([l['num'] for l in r['list']])
            ),
            list=Field(
                _sortkey=lambda r: -r['num'],
                _where=lambda r: r['num'] < 4
            ),
        )

        data = [
            {'num': 1},
            {'num': 2},
            {'num': 3},
            {'num': 4},
            {'num': 5}
        ]

        self.assertEqual(a.feed(data).get(), dict([
            ('sum', 15),
            ('something', 2),
            ('maxinlist', 3),
            ('list', [{'num': 3}, {'num': 2}, {'num': 1}]),
        ]))

    # @unittest.skip('test')
    def test_complex(self):
        def include_client(client):
            return len(client['free']) + len(client['credit'])

        def get_currencies(client):
            currs = list(set([f['currencyID'] for f in client['free']] +
                             [c['currencyID'] for c in client['credit']]))
            currs.sort()
            return currs

        def balanceitem(o):
            return 'free' in o or 'credit' in o

        a = Dict(
            _where=lambda x: x['clientID'] != 444,
            balances=GroupByFields(
                'clientID',
                _where=balanceitem,
                _having=include_client,
                _post_sortkey=lambda o: o['clientID'],
                field=Dict(
                    clientID=PickField('clientID'),
                    free=GroupByFields(
                        'currencyID',
                        _where=lambda o: 'free' in o,
                        _having=lambda o: o['amount'],
                        _post_sortkey=lambda o: o['currencyID'],
                        field=Dict(
                            currencyID=PickField('currencyID'),
                            amount=SumField('free')
                        )
                    ),
                    credit=GroupByFields(
                        'currencyID',
                        _where=lambda o: 'credit' in o,
                        _having=lambda o: o['amount'],
                        _post_sortkey=lambda o: o['currencyID'],
                        field=Dict(
                            currencyID=PickField('currencyID'),
                            amount=SumField('credit')
                        )
                    ),
                    currencies=Computed(get_currencies)
                )
            ),
            clientDetails=GroupByFields(
                'clientID',
                _where=lambda o: 'clientCode' in o,
                _sortkey=lambda o: o['clientCode'],
                field=Dict(
                    clientID=PickField('clientID'),
                    clientCode=PickField('clientCode'),
                )
            )
        )

        data = [
            {'clientID': 222, 'currencyID': 'EUR', 'free': 123},
            {'clientID': 111, 'currencyID': 'EUR', 'free': 123},
            {'clientID': 111, 'currencyID': 'EUR', 'credit': 50},
            {'clientID': 111, 'currencyID': 'PLN', 'free': 20},
            {'clientID': 111, 'currencyID': 'EUR', 'free': 2},
            {'clientID': 111, 'currencyID': 'PLN', 'free': -18},
            {'clientID': 111, 'currencyID': 'PLN', 'free': -2},
            {'clientID': 222, 'currencyID': 'EUR', 'free': -123},
            {'clientID': 333, 'currencyID': 'GBP', 'free': 200},
            {'clientID': 333, 'currencyID': 'EUR', 'free': 123},
            {'clientID': 444, 'currencyID': 'EUR', 'free': 2000},
            {'clientID': 333, 'clientCode': '00333'},
            {'clientID': 111, 'clientCode': '00111'},
        ]

        self.assertEqual(a.feed(data).get(), dict([
            ('balances', [
                dict([
                    ('clientID', 111),
                    ('free', [
                        dict([('currencyID', 'EUR'), ('amount', 125)]),
                    ]),
                    ('credit', [
                        dict([('currencyID', 'EUR'), ('amount', 50)]),
                    ]),
                    ('currencies', ['EUR']),
                ]),
                dict([
                    ('clientID', 333),
                    ('free', [
                        dict([('currencyID', 'EUR'), ('amount', 123)]),
                        dict([('currencyID', 'GBP'), ('amount', 200)]),
                    ]),
                    ('credit', []),
                    ('currencies', ['EUR', 'GBP']),
                ]),
            ]),
            ('clientDetails', [
                dict([('clientID', 111), ('clientCode', '00111')]),
                dict([('clientID', 333), ('clientCode', '00333')]),
            ]),
        ]))


# @unittest.skip('only for performance measuring')
class LongTest(unittest.TestCase):
    def test_many(self):
        def include_client(client):
            return len(client['free']) + len(client['credit'])

        def get_currencies(client):
            currs = list(set([f['currencyID'] for f in client['free']] +
                             [c['currencyID'] for c in client['credit']]))
            currs.sort()
            return currs

        def balanceitem(o):
            return 'free' in o or 'credit' in o

        a = Dict(
            _where=lambda x: x['clientID'] != 444,
            balances=GroupByFields(
                'clientID',
                _where=balanceitem,
                _having=include_client,
                _post_sortkey=lambda o: o['clientID'],
                field=Dict(
                    clientID=PickField('clientID'),
                    free=GroupByFields(
                        'currencyID',
                        _where=lambda o: 'free' in o,
                        _having=lambda o: o['amount'],
                        _post_sortkey=lambda o: o['currencyID'],
                        field=Dict(
                            currencyID=PickField('currencyID'),
                            amount=SumField('free')
                        )
                    ),
                    credit=GroupByFields(
                        'currencyID',
                        _where=lambda o: 'credit' in o,
                        _having=lambda o: o['amount'],
                        _post_sortkey=lambda o: o['currencyID'],
                        field=Dict(
                            currencyID=PickField('currencyID'),
                            amount=SumField('credit')
                        )
                    ),
                    currencies=Computed(get_currencies)
                )
            )
        )

        clients = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        currencies = ['EUR', 'PLN', 'RON']
        i = 0
        data = []
        while i < 50000:
            clientID = random.choice(clients)
            currencyID = random.choice(currencies)
            free = decimal.Decimal(random.randint(100, 1000))
            credit = decimal.Decimal(random.randint(100, 1000))
            data.append({'clientID': clientID, 'currencyID': currencyID,
                         'free': free, 'credit': credit})
            i += 1

        print('start')
        print(a.feed(data).get())
        print('end')
