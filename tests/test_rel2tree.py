import unittest

from rel2tree import Adder


class SimpleTestCase(unittest.TestCase):
    def test_adder(self):
        a = Adder(2)
        self.assertEqual(a.add(1), 2, 'something went wrong')
