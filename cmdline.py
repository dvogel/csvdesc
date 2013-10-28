# -*- coding: utf-8 -*-

import argparse

__all__ = ['CmdLineParser']

CmdLineParser = argparse.ArgumentParser(description='Summarize field types and values observed in (a sample of) a CSV file.')

sampling_style = CmdLineParser.add_mutually_exclusive_group()

sampling_style.add_argument('--firstn',
                            action='store_const',
                            dest='sampling',
                            const='firstn',
                            help='Examine only the first N record (most efficient).')

sampling_style.add_argument('--reservoir',
                            action='store_const',
                            dest='sampling',
                            const='reservoir',
                            help='Examine a random N records (for fixed sample size.')

sampling_style.add_argument('--percentage',
                            action='store_const',
                            dest='sampling',
                            const='percentage',
                            help='Examine a random, approximate percentage of records (for variable sample size).')

CmdLineParser.add_argument('--samplesize',
                           action='store',
                           dest='samplesize',
                           metavar='N',
                           type=int,
                           default=1000,
                           help='Number or percentage (as whole number) of records to sample (default: 1000).')

CmdLineParser.add_argument('--loglevel',
                           action='store',
                           dest='loglevel',
                           choices=('debug', 'info', 'notice', 'warning', 'error', 'critical'))

CmdLineParser.add_argument('files',
                           metavar='FILE',
                           nargs='+')

