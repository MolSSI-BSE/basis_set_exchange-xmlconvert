#!/usr/bin/env python3

import json
import os
import sys
import glob

import bse
import numpy as np


# merge from src -> into dest
src = sys.argv[1]
dest = sys.argv[2]

src_base = os.path.splitext(src)[0]
dest_base = os.path.splitext(dest)[0]

element_files = glob.glob("*.element.json")
table_files = glob.glob("*.table.json")

if not os.path.isfile(src):
    raise RuntimeError("Source file does not exist")
if not os.path.isfile(dest):
    raise RuntimeError("Destination file does not exist")

src_data = bse.read_json_by_path(src)
dest_data = bse.read_json_by_path(dest)

src_elements = src_data['basisSetElements']
dest_elements = dest_data['basisSetElements']

for k,v in src_elements.items():
    if not k in dest_elements:
        dest_elements[k] = v
    else:
        dest_el = dest_elements[k]
        dest_el['elementReferences'].extend(v['elementReferences'])
        dest_el['elementElectronShells'].extend(v['elementElectronShells'])

# Handle a rename    
for f in element_files:
    changed = False
    data = bse.read_json_by_path(f)
    for k,v in data['basisSetElements'].items():
        if src_base in v['elementComponents']:
            changed = True
            print("Found in {} {}".format(f, k))
            v['elementComponents'] = [ dest_base if x == src_base else x for x in v['elementComponents'] ]

    if changed:
        os.rename(f, f + ".old")
        bse.write_basis_file(f, data)

# Rename the old file
os.rename(src, src + '.old')
