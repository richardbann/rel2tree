import unittest

from rel2tree import f


class Test(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(f.t(sum)([1, 2, 3, 4]), 10)
        self.assertEqual(f.map(lambda x: x + 1)([1, 2, 3, 4]), [2, 3, 4, 5])
        self.assertEqual(f.filter(lambda x: x % 2 == 0)([1, 2, 3, 4]), [2, 4])
        self.assertEqual(f.sort()([3, 2, 1]), [1, 2, 3])
        self.assertEqual(f.sort(lambda x: -x)([1, 2, 3, 4]), [4, 3, 2, 1])
        self.assertEqual(f.dict({"c": 1})([]), {"c": 1})
        self.assertEqual(
            f.groupby(
                lambda x: x["name"],
                f.dict(
                    {"name": f.groupkey(), "sum": f.map(lambda x: x["value"]).t(sum)}
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
            f.groupby(lambda x: x["name"])([{"name": "Jane", "value": 5}]),
            [[{"name": "Jane", "value": 5}]],
        )
        self.assertEqual(
            f.groupby(lambda x: x["name"], f.dict({"name": f.groupkey(1)}))(
                [{"name": "Jane", "value": 5}]
            ),
            [{"name": None}],
        )
        self.assertEqual(
            f.groupby(lambda x: x % 2, f.distinct())([1, 1, 2, 3, 4, 4]),
            [[1, 3], [2, 4]]
        )
        self.assertEqual(
            f.groupby(lambda x: x[0], f.groupby(lambda x: x[1]))([
                (1, "a"),
                (1, "b"),
                (1, "a"),
                (2, "a"),
                (2, "b"),
                (2, "b"),
            ]),
            [
                [
                    [(1, "a"), (1, "a")], [(1, "b")]
                ],
                [
                    [(2, "a")], [(2, "b"), (2, "b")]
                ],
            ]
        )
