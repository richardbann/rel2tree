import unittest

from rel2tree import F, const, groupkey


class Test(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(F().t(sum)([1, 2, 3, 4]), 10)
        self.assertEqual(F().map(lambda x: x + 1)([1, 2, 3, 4]), [2, 3, 4, 5])
        self.assertEqual(F().filter(lambda x: x % 2 == 0)([1, 2, 3, 4]), [2, 4])
        self.assertEqual(F().sort()([3, 2, 1]), [1, 2, 3])
        self.assertEqual(F().sort(lambda x: -x)([1, 2, 3, 4]), [4, 3, 2, 1])
        self.assertEqual(F().dict({"c": const(1)})([]), {"c": 1})
        self.assertEqual(
            F().groupby(
                lambda x: x["name"],
                F().dict(
                    {"name": groupkey(), "sum": F().map(lambda x: x["value"]).t(sum)}
                ),
            )(
                [
                    {"name": "Jane", "value": 5},
                    {"name": "Joe", "value": 2},
                    {"name": "Jane", "value": 1},
                ]
            ),
            [{"name": "Jane", "sum": 6}, {"name": "Joe", "sum": 2}],
        )
        self.assertEqual(
            F().groupby(lambda x: x["name"])([{"name": "Jane", "value": 5}]),
            [[{"name": "Jane", "value": 5}]],
        )
        self.assertEqual(
            F().groupby(lambda x: x["name"], F().dict({"name": groupkey(1)}))(
                [{"name": "Jane", "value": 5}]
            ),
            [{"name": None}],
        )


# import pprint
#
# from rel2tree import F, const, groupkey
#
#
# pprint.pprint(
#     F()
#     .map(lambda x: x + 1)
#     .dict(
#         {
#             "even": F()
#             .groupby(
#                 lambda x: x % 11,
#                 F().dict(
#                     {
#                         "divisor": const(11),
#                         "remainder": groupkey(),
#                         "numbers": F()
#                         .groupby(
#                             lambda x: x % 7,
#                             F().dict(
#                                 {
#                                     "divisor": const(7),
#                                     "remainder": groupkey(),
#                                     "numbers": F(),
#                                     "sum": F().t(sum),
#                                 }
#                             ),
#                         )
#                         .sort(lambda x: x["remainder"]),
#                         "sum": F().t(sum),
#                     }
#                 ),
#             )
#             .sort(lambda x: x["remainder"]),
#             "odd": F()
#             .groupby(
#                 lambda x: x % 7,
#                 F().dict(
#                     {
#                         "divisor": const(7),
#                         "remainder": groupkey(),
#                         "numbers": F(),
#                         "sum": F().t(sum),
#                     }
#                 ),
#             )
#             .sort(lambda x: x["remainder"]),
#         }
#     )(range(100)),
#     width=100,
# )
