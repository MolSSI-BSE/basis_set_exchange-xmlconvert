#!/usr/bin/env python3

import json
import os
import sys
import glob

import bse
import numpy as np


src = sys.argv[1]
dest = sys.argv[2]

src_base = os.path.splitext(src)[0]
dest_base = os.path.splitext(dest)[0]




if os.path.isfile(dest):
    raise RuntimeError("Destination file exists")

os.rename(src, dest)

src_base2 = os.path.splitext(src_base)[0]
dest_base2 = os.path.splitext(dest_base)[0]

element_files = glob.glob("*.element.json")
table_files = glob.glob("*.table.json")

# Rename description file
if os.path.isfile(src_base + '.txt'):
    src_desc_file = src_base + '.txt'
    dest_desc_file = dest_base + '.txt'
    os.rename(src_desc_file, dest_desc_file)

if src.endswith('.table.json'):
    pass

elif src_base.endswith('.element'):
    for f in table_files:
        changed = False
        data = bse.read_json_by_path(f)
        for k,v in data['basisSetElements'].items():
            if v['elementEntry'] == src_base2:
                changed = True
                print("Found in {} {}".format(f, k))
                v['elementEntry'] = dest_base2
        if changed:
            os.rename(f, f + ".old")
            bse.write_basis_file(f, data)
else:
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
