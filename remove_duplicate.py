#!/usr/bin/env python3

import argparse
import json
import os
import sys
import glob

import bse


# Is a dictionary a subset of another?
# https://stackoverflow.com/questions/9323749/python-check-if-one-dictionary-is-a-subset-of-another-larger-dictionary
def is_subset(subset, superset):
    # For dicts
    #return all(item in superset.items() for item in subset.items())

    # For lists
    return all(item in superset for item in subset)


parser = argparse.ArgumentParser()
parser.add_argument('source_file', help='File to use as the master', type=str)
args = parser.parse_args()

# All json files in the current directory
#all_json_files = [ x for x in os.listdir() if os.path.splitext(x)[1] == ".json" ]
all_json_files = glob.glob("bse_xml/*.json")

all_component_files = []
all_atom_files = []

for x in all_json_files:
    if x == args.source_file:
        continue
    elif x.endswith('.element.json'):
        all_atom_files.append(x)
    elif not x.endswith('.table.json'):
        all_component_files.append(x)

# Read in the source file
sdata = bse.read_json_by_path(args.source_file)
sname = os.path.splitext(args.source_file)[0]
selements = sdata['basisSetElements']

# Map of what we replaced or added
replaced_map = {}
added_map = {}

for cfile in all_component_files:
    print("Comparing with {}".format(cfile))
    changed = False

    cdata = bse.read_json_by_path(cfile)
    cname = os.path.splitext(cfile)[0]
    celements = cdata['basisSetElements']

    # Compare by element
    for k in selements.keys():
        if k not in celements:
            continue

        sel = selements[k]
        cel = celements[k]

        if sel == cel:
            changed = True

            # Add to the map
            if not cname in replaced_map:
                replaced_map[cname] = []

            replaced_map[cname].append(k)

            # Remove from the candidate
            celements.pop(k)

        elif is_subset(sel['elementElectronShells'], cel['elementElectronShells']):
            changed = True

            if not cname in added_map:
                added_map[cname] = []

            added_map[cname].append(k)

            # remove only the equivalent shells
            celements[k]['elementElectronShells'] = [
                x for x in cel['elementElectronShells'] if not x in sel['elementElectronShells']
            ]

    # rewrite the candidate file
    if changed:
        os.rename(cfile, cfile + ".old")
        bse.write_basis_file(cfile, cdata)

# print out the replacement map
for k, v in replaced_map.items():
    print("Replaced in {}: {}".format(k, v))
for k, v in added_map.items():
    print("Partially replaced in {}: {}".format(k, v))

# Now go through all the atom basis files, doing replacements
for afile in all_atom_files:
    adata = bse.read_json_by_path(afile)

    changed = False

    for k, v in adata['basisSetElements'].items():
        for i, c in enumerate(v['elementComponents']):
            if c in replaced_map and k in replaced_map[c]:
                v['elementComponents'][i] = sname
                changed = True

            if c in added_map and k in added_map[c]:
                v['elementComponents'].append(sname)
                changed = True

    if changed:
        os.rename(afile, afile + ".old")
        bse.write_basis_file(afile, adata)
