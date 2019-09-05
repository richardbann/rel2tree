import unittest


class Test(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(1, 1)


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
