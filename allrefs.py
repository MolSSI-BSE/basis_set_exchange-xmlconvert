#!/usr/bin/env python3

import json
import os
import sys

import bse


src = sys.argv[1]
js = bse.read_json_basis(src)

allrefs = []

for k,v in js['basisSetElements'].items():
    eref = v['elementReferences']
    allrefs.extend(eref)

done_refs = set()

for r in allrefs:
    if not r in done_refs:
        print(r)
        done_refs.add(r)
