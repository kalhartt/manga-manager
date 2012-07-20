#!/usr/bin/env python2
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('integers', metavar='N', nargs='+',
                   help='an integer for the accumulator')

args = parser.parse_args()
print args
