
import json
import os
import sys
import glob
import time

import bse

ref_dir = 'refs'


def find_Z(js, Z):
    ret = [] 
    for c in js['citations']:
        if int(Z) in c['Z']:
            ret.append(c)

    return ret

# files to search
file_list = glob.glob("*.json")

for f in file_list:
    fbase = os.path.splitext(f)[0]

    # "Description"
    txtfile = fbase + '.txt'
    if os.path.isfile(txtfile):
        with open(txtfile, 'r') as ftmp:
            file_desc = ftmp.read()

    file_data = bse.read_json_basis(f)

    # for each element
    for el,data in file_data['basisSetElements'].items():
        el = int(el)

        if not 'elementReferences' in data:
            continue

        elref = data['elementReferences']
        elsym = bse.lut.element_sym_from_Z(el)

        if len(elref) > 1:
            raise RuntimeError("Multiple references")

        elref = elref[0]

        reffile = os.path.join(ref_dir, elref + '.json')
        file_ref_json = None
        file_ref_raw = None
        if os.path.isfile(reffile):
            with open(reffile, 'r') as ftmp:
                file_ref_json = json.loads(ftmp.read())
                file_ref_raw = file_ref_json['original']
        else:
            continue

        elref_data = find_Z(file_ref_json, el) 
        new_references = []

        for d in elref_data:
            if 'article' in d:
                new_references.append(d['article'])

        print("    Articles: ", new_references)
        data['elementReferences'] = new_references

    os.rename(f, f+'.old')
    bse.write_json_basis(f, file_data)
    
