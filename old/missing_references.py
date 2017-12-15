
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
filename = sys.argv[1]

fbase = os.path.splitext(filename)[0]

with open(filename, 'r') as ftmp:
    file_data = json.loads(ftmp.read())

# "Description"
txtfile = fbase + '.txt'
if os.path.isfile(txtfile):
    with open(txtfile, 'r') as ftmp:
        file_desc = ftmp.read()

# Actual reference data
with open('refs/REFERENCES.json', 'r') as ftmp:
    refdata = json.loads(ftmp.read())

for el,data in file_data['basisSetElements'].items():
    el = int(el)

    if not 'elementReferences' in element:
        continue

    elref = element['elementReferences']
    elsym = bse.lut.element_sym_from_Z(el)
    print("Element: ", el, " ", bse.lut.normalize_element_symbol(elsym))


    for ref in elref:
        reffile = os.path.join(ref_dir, elref[0] + '.json')
        if not os.path.isfile(reffile):
            print("REFERENCE NOT FOUND")
            
            with open(reffile, 'r') as ftmp:
                file_ref_json = json.loads(ftmp.read())
            file_ref_raw = file_ref_json['original']

    if file_ref_json:
        elref_data = find_Z(file_ref_json, el) 

        #print("    References:")
        if len(elref_data) == 0:
            # Information was not parsed for this element. Prompt for it
            print("        NOT FOUND")
            doi = prompt_doi("hi")
        else:
            for d in elref_data:
                bad = False
                orig = d['original']

                if not 'article' in d:
                    art = '                NO ARTICLE FOUND'
                    doi = prompt_doi(d['original'])
                else:
                    art = d['article']

    print()


    
