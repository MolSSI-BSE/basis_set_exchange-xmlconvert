
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

refdata = bse.read_references("refs/REFERENCES.json")

for f in file_list:
    fbase = os.path.splitext(f)[0]
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
        #elif len(elref == 0)
        #    continue

        elref = elref[0]

        reffile = os.path.join(ref_dir, elref + '.json')
        file_ref_json = None
        if os.path.isfile(reffile):
            with open(reffile, 'r') as ftmp:
                file_ref_json = json.loads(ftmp.read())
        else:
            print("Missing file {}".format(reffile))
            continue

        elref_data = find_Z(file_ref_json, el) 
        new_references = []

        for d in elref_data:
            if 'article' in d:
                new_references.append(d['article'])
                if not d['article'] in refdata:
                    print("File: ", f)
                    print("reffile: ", reffile)
                    raise RuntimeError("Reference {} not found in REFERENCES".format(d['article']))
            else:
                print("No article: {}".format(reffile))

        #print("    Articles: ", new_references)
        data['elementReferences'] = new_references

    #os.rename(f, f+'.old')
    bse.write_json_basis(f, file_data)
    
