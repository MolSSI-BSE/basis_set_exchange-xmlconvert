#!/usr/bin/env python3

import json
import re

with open('REFERENCES.json', 'r') as f:
    js = json.load(f)

doi_map = {}

for k,v in js.items():
    if "DOI" in v:
        doi = v["DOI"].strip().lower()
        doi = doi.lower()
        test_doi = re.sub(r'[^\w]', '', doi)

        if test_doi in doi_map:
            doi_map[test_doi].append(k)
        else:
            doi_map[test_doi] = [ k ]
        

for k,v in doi_map.items():
    if len(v) > 1:
        print("Duplicates:")
        for item in v:
            print("        {:20}: {}".format(item, js[item]['DOI']))



