import json
import os
import sys
import glob
import time
import requests

import bse
from bse import curate


reffile = sys.argv[1]
search_str = sys.argv[2]

refs = bse.read_references(reffile)

if search_str.lower().startswith("doi"):
    refinfo = curate.query_crossref_doi(search_str[4:])
else:
    refinfo = curate.query_crossref(search_str)

if not refinfo:
    raise RuntimeError("Crossref didn't find useful data (or none at all)")


first_author = refinfo['authors'][0]
last_name = first_author.split()[-1]
key = curate.create_reference_key(refs, last_name, refinfo['year'])
curate.print_citation(key, refinfo)

if 'DOI' in refinfo:
    existing = curate.find_ref_by_doi(refs, refinfo['DOI'])
    if existing:
        print("Found existing key for doi {} : {}".format(refinfo['DOI'], existing))
        quit()


refs[key] = refinfo

while True:
    ans = input("Proceed? (y/n) -> ")
    ans = ans.lower()
    if ans == 'y' or ans == 'n':
        break

if ans == 'y':
    newfile = reffile + '.new'
    bse.write_references(newfile, refs)
    print("Changes written to ", newfile)
else:
    print("No changes made")

