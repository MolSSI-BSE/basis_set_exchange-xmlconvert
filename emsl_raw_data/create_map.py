#!/usr/bin/env python3
import sys
import shlex

lines = [ l.strip() for l in open('published.txt', 'r').readlines() ]
lines2 = [ [ x.rstrip(', ') for x in shlex.split(l) ] for l in lines ]

for l in lines2:
    print('{:48} {}'.format(l[1], l[0]))
