import unittest
from collections import OrderedDict

from rel2tree.utils import Sum, SumField, List, GroupByFields, GroupingField
from rel2tree.core import Struct, Constant, Computed, GroupBy


class SimpleTestCase(unittest.TestCase):

    # @unittest.skip('test')
    def test_aggregator_simple(self):
        a = Sum()
        r = a._create([1, 2, 3])
        self.assertEqual(r, 6)

    # @unittest.skip('test')
    def test_aggregator_where(self):
        a = Sum(_where=lambda r: r % 2 == 0)
        r = a._create([1, 2, 3])
        self.assertEqual(r, 2)

    # @unittest.skip('test')
    def test_sumfield(self):
        a = SumField('n')
        r = a._create([{'n': 1}, {'n': 2}, {'n': 3}])
        self.assertEqual(r, 6)

    # @unittest.skip('test')
    def test_simple_struct(self):
        a = Struct(
            sum=SumField('num'),
            something=Constant(2),
            maxinlist=Computed(
                lambda r: max([l['num'] for l in r['list']])
            ),
            list=List(
                _sortkey=lambda r: -r['num'],
                _having=lambda r: r['num'] < 4
            ),
        )

        data = [
            {'num': 1},
            {'num': 2},
            {'num': 3},
            {'num': 4},
            {'num': 5}
        ]

        self.assertEqual(a._create(data), OrderedDict([
            ('sum', 15),
            ('something', 2),
            ('maxinlist', 3),
            ('list', [{'num': 3}, {'num': 2}, {'num': 1}]),
        ]))

    # @unittest.skip('test')
    def test_groupby(self):
        a = Struct(
            type=Constant('TEST'),
            clients=GroupBy(
                _sortkey=lambda r: r['clientID'],
                _grouping=lambda obj: obj['client_id'],
                clientID=GroupingField('client_id'),
                sumorders=SumField('quantity'),
            ),
            sum=SumField('quantity'),
            sumbigs=SumField(
                'quantity',
                _where=lambda o: o['quantity'] >= 50)
        )

        data = [
            {'client_id': 2, 'quantity': 100},
            {'client_id': 1, 'quantity': 10},
            {'client_id': 1, 'quantity': 20},
        ]

        self.assertEqual(a._create(data), OrderedDict([
            ('type', 'TEST'),
            ('clients', [{'clientID': 1, 'sumorders': 30},
                         {'clientID': 2, 'sumorders': 100}]),
            ('sum', 130),
            ('sumbigs', 100),
        ]))

    # @unittest.skip('test')
    def test_groupbyfields(self):
        a = GroupByFields(
            _sortkey=lambda r: r['client_id'],
            client_id=GroupingField('client_id'),
            sumorders=SumField('quantity'),
        )

        data = [
            {'client_id': 2, 'quantity': 100},
            {'client_id': 1, 'quantity': 10},
            {'client_id': 1, 'quantity': 20},
        ]

        self.assertEqual(a._create(data), [
            OrderedDict([('client_id', 1), ('sumorders', 30)]),
            OrderedDict([('client_id', 2), ('sumorders', 100)]),
        ])

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

        a = Struct(
            _where=lambda x: x['clientID'] != 444,
            balances=GroupByFields(
                _where=balanceitem,
                _having=include_client,
                _sortkey=lambda o: o['clientID'],
                clientID=GroupingField('clientID'),
                free=GroupByFields(
                    _where=lambda o: 'free' in o,
                    _having=lambda o: o['amount'],
                    _sortkey=lambda o: o['currencyID'],
                    currencyID=GroupingField('currencyID'),
                    amount=SumField('free'),
                ),
                credit=GroupByFields(
                    _where=lambda o: 'credit' in o,
                    _having=lambda o: o['amount'],
                    _sortkey=lambda o: o['currencyID'],
                    currencyID=GroupingField('currencyID'),
                    amount=SumField('credit'),
                ),
                currencies=Computed(get_currencies),
            ),
            clientDetails=GroupByFields(
                _where=lambda o: 'clientCode' in o,
                _sortkey=lambda o: o['clientCode'],
                clientID=GroupingField('clientID'),
                clientCode=GroupingField('clientCode'),
            )
        )

        data = [
            {'clientID': 111, 'currencyID': 'EUR', 'free': 123},
            {'clientID': 111, 'currencyID': 'EUR', 'credit': 50},
            {'clientID': 111, 'currencyID': 'PLN', 'free': 20},
            {'clientID': 111, 'currencyID': 'EUR', 'free': 2},
            {'clientID': 111, 'currencyID': 'PLN', 'free': -18},
            {'clientID': 222, 'currencyID': 'EUR', 'free': 123},
            {'clientID': 111, 'currencyID': 'PLN', 'free': -2},
            {'clientID': 222, 'currencyID': 'EUR', 'free': -123},
            {'clientID': 333, 'currencyID': 'EUR', 'free': 123},
            {'clientID': 333, 'currencyID': 'GBP', 'free': 200},
            {'clientID': 444, 'currencyID': 'EUR', 'free': 2000},
            {'clientID': 333, 'clientCode': '00333'},
            {'clientID': 111, 'clientCode': '00111'},
        ]

        # import json
        # from rel2tree.encoders import DecimalJSONEncoder
        # print(json.dumps(a._create(data), cls=DecimalJSONEncoder, indent=2))

        self.assertEqual(a._create(data), OrderedDict([
            ('balances', [
                OrderedDict([
                    ('clientID', 111),
                    ('free', [
                        OrderedDict([('currencyID', 'EUR'), ('amount', 125)]),
                    ]),
                    ('credit', [
                        OrderedDict([('currencyID', 'EUR'), ('amount', 50)]),
                    ]),
                    ('currencies', ['EUR']),
                ]),
                OrderedDict([
                    ('clientID', 333),
                    ('free', [
                        OrderedDict([('currencyID', 'EUR'), ('amount', 123)]),
                        OrderedDict([('currencyID', 'GBP'), ('amount', 200)]),
                    ]),
                    ('credit', []),
                    ('currencies', ['EUR', 'GBP']),
                ]),
            ]),
            ('clientDetails', [
                OrderedDict([('clientID', 111), ('clientCode', '00111')]),
                OrderedDict([('clientID', 333), ('clientCode', '00333')]),
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

        a = Struct(
            _where=lambda x: x['clientID'] != 444,
            balances=GroupByFields(
                _where=balanceitem,
                _having=include_client,
                _sortkey=lambda o: o['clientID'],
                clientID=GroupingField('clientID'),
                free=GroupByFields(
                    _where=lambda o: 'free' in o,
                    _having=lambda o: o['amount'],
                    _sortkey=lambda o: o['currencyID'],
                    currencyID=GroupingField('currencyID'),
                    amount=SumField('free'),
                ),
                credit=GroupByFields(
                    _where=lambda o: 'credit' in o,
                    _having=lambda o: o['amount'],
                    _sortkey=lambda o: o['currencyID'],
                    currencyID=GroupingField('currencyID'),
                    amount=SumField('credit'),
                ),
                currencies=Computed(get_currencies),
            ),
        )

        import random
        clients = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        currencies = ['EUR', 'PLN', 'RON']
        i = 0
        data = []
        while i < 50000:
            clientID = random.choice(clients)
            currencyID = random.choice(currencies)
            # free = decimal.Decimal(random.randint(100, 1000))
            # credit = decimal.Decimal(random.randint(100, 1000))
            free = random.randint(100, 1000)
            credit = random.randint(100, 1000)

            data.append({'clientID': clientID, 'currencyID': currencyID,
                         'free': free, 'credit': credit})
            i += 1

        import json
        from rel2tree.encoders import DecimalJSONEncoder
        print(json.dumps(a._create(data), cls=DecimalJSONEncoder, indent=2))
