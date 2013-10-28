# -*- coding: utf-8 -*-

import os
import random
import unittest
from decimal import Decimal
from csvdesc import describe_file, SamplingStyles

def describe_fixture(name, *args, **kwargs):
    srcdir = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(srcdir, 'fixtures', name)
    return describe_file(path, *args, **kwargs)

class TestGuessCorrectness(unittest.TestCase):

    def setUp(self):
        pass

    def test_single_column_int(self):
        guesses = describe_fixture('int1.csv')
        ((field, guess),) = guesses.items()
        self.assertEqual(field, 'i')
        self.assertEqual(guess.observations, 3)
        self.assertEqual(guess.type, int)

    def test_single_column_bool(self):
        ((field, guess),) = describe_fixture('bool1.csv').items()
        self.assertEqual(field, 'b')
        self.assertEqual(guess.observations, 6)
        self.assertEqual(guess.type, bool)

    def test_all_types_together(self):
        guesses = describe_fixture('eachtype.csv')
        bools = guesses['BOOLEAN']
        ints = guesses['INTEGER']
        decs = guesses['DECIMAL']
        strings = guesses['STRING']

        self.assertEqual(bools.type, bool)
        self.assertEqual(ints.type, int)
        self.assertEqual(decs.type, Decimal)
        self.assertEqual(strings.type, str)

    def test_single_boolean_int_is_int(self):
        guesses = describe_fixture('int1.csv', SamplingStyles.FirstN(1))
        ((field, guess),) = guesses.items()
        self.assertEqual(field, 'i')
        self.assertEqual(guess.observations, 1)
        self.assertEqual(guess.values['1'], 1)
        self.assertEqual(guess.type, int)

class TestSampling(unittest.TestCase):
    def test_reservoir_underrun(self):
        guesses = describe_fixture('int1.csv', SamplingStyles.Reservior(1000))
        self.assertEqual(guesses['i'].observations, 3)

    def test_reservoir_exactsize(self):
        guesses = describe_fixture('int1.csv', SamplingStyles.Reservior(3))
        self.assertEqual(guesses['i'].observations, 3)

    def test_reservoir_overrun(self):
        guesses = describe_fixture('longfile1.csv', SamplingStyles.Reservior(100))
        self.assertEqual(guesses['field'].observations, 100)

if __name__ == '__main__':
    unittest.main()

