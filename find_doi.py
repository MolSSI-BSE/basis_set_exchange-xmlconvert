
import json
import os
import sys
import glob
import time
import requests

import bse


def query_crossref(query):
    # Requested by crossref API
    headers = {
        'User-Agent': 'BSEConverter 1.0 (mailto:bpp4@vt.edu)'
    }

    r = requests.get('https://api.crossref.org/works', params={'query': query}, headers=headers)
    if r.status_code != 200:
        return None
    else:
        j = json.loads(r.text)
        r1 = j['message']['items'][0]

        ret = { 'title' : r1['title'][0],
                'year' : r1['published-print']['date-parts'][0][0],
                'journal' : r1['container-title'][0],
                'DOI' : r1['DOI'],
               }

        if 'author' in r1:
            ret['author'] = [ x['given'] + " " + x['family'] for x in r1['author'] ]
        else:
            ret['author'] = [ "unknown" ]

        if 'volume' in r1:
            ret['volume'] = r1['volume']
        if 'page' in r1:
            ret['page'] = r1['page']
        
        return ret


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
                'year' : r1['published-print']['date-parts'][0][0],
                'journal' : r1['container-title'][0],
                'DOI' : r1['DOI'],
               }

        ret['author'] = [ x['given'] + " " + x['family'] for x in r1['author'] ]

        if 'volume' in r1:
            ret['volume'] = r1['volume']
        if 'page' in r1:
            ret['page'] = r1['page']
        
        return ret

def print_cr_result(query, result):
    print("    " + result['title'])
    print('    Authors: ')
    for a in result['author']:
        print('        {}'.format(a))

    if 'volume' in result:
        print('    {}, v{} ({}), pp {}'.format(result['journal'], result['volume'], result['year'], result['page'] if 'page' in result else ""))
    else:
        print('    {}, ({})'.format(result['journal'], result['year']))
    print("    DOI: ", result['DOI'])


def prompt_ok():
    while True:
        valid = ['s', 'y', 'n']
        ok = input("    --> Does this look correct [{}]? ".format(''.join(valid)))
        ok = ok.lower()
        if ok in valid:
            return ok


reffile = sys.argv[1]

with open(reffile, 'r') as f:
    refdata = json.loads(f.read())

for k,v in refdata.items():
    if not "DOI" in v or v["DOI"] == "":
        print()
        print()
        print("{} missing DOI".format(k))
        print(v['original'])
        res = query_crossref(v["original"])
        print_cr_result(v["original"], res)
        print()
        ok = prompt_ok()
        if ok == 's':
            continue
        elif ok == 'y':
            refdata[k]['DOI'] = res['DOI']
            bse.write_references(reffile + ".new", refdata)
        elif ok == 'n':
            doi = input("    --> Input DOI: ")
            res = query_crossref_doi(doi)
            print_cr_result(v["original"], res)
            print()
            ok = prompt_ok()
            if ok == 's':
                continue
            elif ok == 'n':
                raise RuntimeError("You are on your own")

            refdata[k]['DOI'] = res['DOI']
            bse.write_references(reffile + ".new", refdata)
                

