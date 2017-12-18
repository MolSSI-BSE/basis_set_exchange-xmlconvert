
import json
import os
import sys
import glob
import time
import requests

import bse


def query_crossref_doi(doi):
    # Requested by crossref API
    headers = {
        'User-Agent': 'BSEConverter 1.0 (mailto:bpp4@vt.edu)'
    }

    r = requests.get('https://api.crossref.org/works/'+doi, headers=headers)
    if r.status_code != 200:
        return None
    else:
        j = json.loads(r.text)
        r1 = j['message']

        ret = { 'title' : r1['title'][0],
                'journal' : r1['container-title'][0],
                'DOI' : r1['DOI'],
               }

        if 'published-print' in r1:
            ret['year'] = r1['published-print']['date-parts'][0][0]

        ret['authors'] = [ x['given'] + " " + x['family'] for x in r1['author'] ]

        if 'volume' in r1:
            ret['volume'] = r1['volume']
        if 'page' in r1:
            ret['page'] = r1['page']
        
        return ret


def prompt_ok():
    while True:
        valid = ['y', 'n']
        ok = input("    --> Does this look correct [{}]? ".format(''.join(valid)))
        ok = ok.lower()
        if ok == '':
            return 'y'
        if ok in valid:
            return ok

def print_cr_result(query, result):
    print("    " + result['title'])
    print('    Authors: ')
    for a in result['authors']:
        print('        {}'.format(a))

    if 'volume' in result:
        print('    {}, v{} ({}), pp {}'.format(result['journal'], result['volume'], result['year'] if 'year' in result else "MISSING", result['page'] if 'page' in result else ""))
    else:
        print('    {}, ({})'.format(result['journal'], result['year'] if 'year' in result else "MISSING"))
    print("    DOI: ", result['DOI'])



reffile = sys.argv[1]
fields = [ 'title', 'authors', 'journal', 'volume', 'page', 'year', 'DOI' ]
fields2 = [ 'title', 'authors', 'volume', 'page', 'year', 'DOI' ]

with open(reffile, 'r') as f:
    refdata = json.loads(f.read())

number = len(refdata.keys())
count = 0

for k,v in refdata.items():
    count += 1
    print("{}/{} Key: {}".format(count, number, k))
    if not "DOI" in v or v["DOI"] == "":
        print("MISSING DOI: {}".format(k))
        continue
    if 'CR_VERIFIED' in v and v['CR_VERIFIED'] == True:
        print("Already done")
        continue

    res = query_crossref_doi(v["DOI"])
    print()
    print_cr_result(v["DOI"], res)
    print()

    # Print comparison:
    all_same = True
    for field in fields:
        if field in v:
            print("Old {:10}: {}".format(field, v[field]))
        else:
            print("Old {:10}: MISSING".format(field))

        if field in res:
            print("New {:10}: {}".format(field, res[field]))
        else:
            print("New {:10}: MISSING".format(field))

    for field in fields2:
        if field in v and field in res:
            if v[field] != res[field]:
                all_same = False
        else:
            all_same = False

    if not all_same:
        ok = prompt_ok()
        if ok == 'y':
            print("Replacing...")
            for field in fields:
                if field in res:
                    refdata[k][field] = res[field] 
            refdata[k]["CR_VERIFIED"] = True
            bse.write_references(reffile + ".new", refdata)
        elif ok == 'n':
            print("Skipping!")
    else:
        # Some are the same but we skipped
        for field in fields2:
            refdata[k][field] = res[field] 
        refdata[k]["CR_VERIFIED"] = True
        bse.write_references(reffile + ".new", refdata)
        print("Automerging...")

