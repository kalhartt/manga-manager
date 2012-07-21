#!/usr/bin/env python2
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-u', '--u1',  action='store', nargs='+',
                   help='an integer for the accumulator')
parser.add_argument('-t', '--t1' , action='store', nargs='*',
                   help='an integer for the accumulator')

args = parser.parse_args()
print args
