#!/usr/bin/env python3

import json
import os
import sys
import glob
import copy

import bse
import numpy as np


src = sys.argv[1]

src_base = os.path.splitext(src)[0]

element_files = { f: bse.read_json_basis(f) for f in glob.glob("*.element.json") }

js = bse.read_json_basis(src)

allrefs = []

for k,v in js['basisSetElements'].items():
    eref = v['elementReferences']
    if len(eref) > 1:
        raise RuntimeError("Found {} references for {}".format(len(eref), k))
    if not eref in allrefs:
        allrefs.append(eref)

for ref in allrefs:
    newjs = copy.deepcopy(js)
    elements_in_ref = [ k for k,v in newjs['basisSetElements'].items() if v['elementReferences'] == ref ]
    newjs['basisSetElements'] = { k:v for k,v in newjs['basisSetElements'].items() if k in elements_in_ref }
    newjs['basisSetReferences'] = ref
    for el,v in newjs['basisSetElements'].items():
        v.pop('elementReferences')
    
    if len(ref) == 0:
        refname = "noref"
    else:
        refname = '_'.join(ref)

    new_filename = src_base + "_" + refname + ".json"
    print()
    print("New filename: ", new_filename)
    print("Ref(s): ", ref)
    print("Elements in ref: ", elements_in_ref)

    bse.write_json_basis(new_filename, newjs)

    # Go through all the aggregate files and rename
    for el,v in element_files.items():
        for z in elements_in_ref:
            if z in v['basisSetElements']:
                comps = v['basisSetElements'][z]['elementComponents']
                if src in comps:
                    idx = comps.index(src)
                    comps[idx] = new_filename

# Save all the aggregate files
for k,v in element_files.items():
    bse.write_json_basis(k, v) 

os.rename(src, src + ".old")
