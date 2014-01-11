# -*- coding: utf-8 -*-

import os
import sys
import csv
import random
import logging
import itertools
import yaml
from cmdline import CmdLineParser
from copy import deepcopy
from decimal import Decimal, InvalidOperation
from collections import namedtuple, defaultdict

__all__ = ['SamplingStyles',
           'describe_fileobj',
           'describe_file']

BOOLEAN_STRINGS = ['yes', 'no', 'true', 'false', 't', 'f', '0', '1', '-1']
BOOLEAN_VALUES = ['yes', 'no', 'true', 'false', 't', 'f', '0', '1', '-1', 0, 1, -1, True, False]

class SamplingStyles(object):
    FirstN = namedtuple('FirstN', ['N'])
    Reservior = namedtuple('Reservior', ['N'])
    RandomPercentage = namedtuple('RandomPercentage', ['P'])
    Population = namedtuple('Population', [])

def bifurcate(things, predicate):
    truthy = []
    falsey = []
    for thing in things:
        if predicate(thing):
            truthy.append(thing)
        else:
            falsey.append(thing)
    return (truthy, falsey)

def reservior_sample(iter, n):
    res = []
    float_n = float(n)
    for (i, value) in enumerate(iter, start=1):
        if i <= n:
            res.append(value)
        else:
            selection_p = float_n / i
            replacement_p = random.random()
            if selection_p > replacement_p:
                offset = random.randint(0, n - 1)
    return res

def possible_types(value):
    possibilities = []

    try:
        int_value = int(value)
        possibilities.append(int)
    except ValueError:
        pass

    try:
        decimal_value = Decimal(value)
        possibilities.append(Decimal)
    except InvalidOperation:
        pass

    if value.lower() in BOOLEAN_STRINGS:
        possibilities.append(bool)

    if len(value) > 0:
        possibilities.append(str)

    return possibilities

class TypeGuess(object):
    def __init__(self, guessed_type, observations, types, values):
        self._guessed_type = guessed_type
        self._observations = observations
        self._types = types
        self._values = values
    @property
    def type(self):
        return self._guessed_type
    @property
    def guess(self):
        return self._guessed_type
    @property
    def guessed_type(self):
        return self._guessed_type
    @property
    def observations(self):
        return self._observations
    @property
    def types(self):
        return self._types
    @property
    def values(self):
        return self._values

class TypeGuesser(object):
    def __init__(self):
        self.observations = 0
        self.type_frequencies = defaultdict(int)
        self.value_frequencies = defaultdict(int)

    def update(self, value):
        self.observations += 1
        self.value_frequencies[value] = self.value_frequencies[value] + 1
        types = possible_types(value)
        for type_ in types:
            self.type_frequencies[type_] = self.type_frequencies[type_] + 1
   
    def wrap_guess(self, type_guess):
        return TypeGuess(type_guess,
                         self.observations,
                         self.type_frequencies,
                         self.value_frequencies)

    def guess(self):
        if self.type_frequencies[bool] == self.observations and len(set(self.value_frequencies.keys()) - set(BOOLEAN_VALUES)) == 0:
            first_value = list(itertools.islice(self.value_frequencies.keys(), 1))[0]
            if len(self.value_frequencies) == 1 and first_value in ('0', '1'):
                return self.wrap_guess(int)
            else:
                return self.wrap_guess(bool)
        elif self.type_frequencies[int] == self.observations:
            return self.wrap_guess(int)
        elif self.type_frequencies[Decimal] == self.observations:
            return self.wrap_guess(Decimal)
        else:
            return self.wrap_guess(str)

    def values(self):
        return deepcopy(self.value_frequencies)

def describe_fileobj(fil, sampling_style=None):
    type_guessers = dict()

    reader = csv.DictReader(fil)

    if isinstance(sampling_style, SamplingStyles.Reservior):
        reader = reservior_sample(reader, sampling_style.N)
    elif isinstance(sampling_style, SamplingStyles.FirstN):
        reader = itertools.islice(reader, sampling_style.N)

    for record in reader:
        if isinstance(sampling_style, SamplingStyles.RandomPercentage):
            selection_p = random.random()
            if selection_p > sampling_style.P:
                continue

        for (field, value) in record.items():
            if value is not None:
                guesser = type_guessers.get(field, None)
                if guesser is None:
                    guesser = type_guessers[field] = TypeGuesser()
                guesser.update(value)

    guesses = dict((
        (field, guesser.guess()) for (field, guesser) in type_guessers.items()
    ))
    return guesses

def describe_file(path, *args, **kwargs):
    with open(path, 'r') as fil:
        return describe_fileobj(fil, *args, **kwargs)

def main(sampling_style, paths):
    (existing_paths, missing_paths) = bifurcate(paths, os.path.exists)

    for path in missing_paths:
        print('No such file: {}'.format(path), file=sys.stderr)
    
    output_struct = []
    for path in existing_paths:
        guessed_types = describe_file(path, sampling_style)
        output_struct.append({
            'path': path,
            'types': [
                dict([('field', field),
                      ('type', guess.type.__name__),
                      ('observations', guess.observations)])
                for (field, guess) in guessed_types.items()]
        })

    if len(output_struct) > 0:
        yaml.dump(output_struct, stream=sys.stdout)


log = logging.getLogger(os.path.basename(__file__)
                        if __name__ == "__main__"
                        else __name__)

if __name__ == "__main__":
    args = CmdLineParser.parse_args()
    log.setLevel(getattr(logging, args.loglevel.upper()))
    log.log(log.getEffectiveLevel(),
            'Logging level: %s', args.loglevel.upper())

    if args.sampling == 'reservoir':
        sampling_style = SamplingStyles.Reservior(args.samplesize)
    elif args.sampling == 'firstn':
        sampling_style = SamplingStyles.FirstN(args.samplesize)
    elif args.sampling == 'percentage':
        sampling_style = SamplingStyles.RandomPercentage(float(args.samplesize) / 100)
    else:
        sampling_style = SamplingStyles.Population()

    log.critical('Sampling style: %s', str(sampling_style))

    if len(sys.argv) > 1:
        main(sampling_style, args.files)

