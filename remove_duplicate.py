#!/usr/bin/env python3

import json
import os
import sys
import glob

import bse
import numpy as np

def compare_shell(shell1, shell2):
    if shell1['shellAngularMomentum'] != shell2['shellAngularMomentum']:
        return False
    if shell1['shellFunctionType'] != shell2['shellFunctionType']:
        return False


    # Replace fortran-style 'D' with 'E'
    exponents1 = [ x.replace('D', 'E') for x in shell1['shellExponents'] ]
    exponents2 = [ x.replace('D', 'E') for x in shell2['shellExponents'] ]
    coefficients1 = [ [ x.replace('D', 'E') for x in y ] for y in shell1['shellCoefficients'] ]
    coefficients2 = [ [ x.replace('D', 'E') for x in y ] for y in shell2['shellCoefficients'] ]

    exponents1 = np.array(exponents1).astype(np.float)
    exponents2 = np.array(exponents2).astype(np.float)
    coefficients1 = np.array(coefficients1).astype(np.float)
    coefficients2 = np.array(coefficients2).astype(np.float)

    if exponents1.shape != exponents2.shape:
        return False
    if coefficients1.shape != coefficients2.shape:
        return False
    if not np.allclose(exponents1, exponents2, rtol=1e-10):
        return False
    if not np.allclose(coefficients1, coefficients2, rtol=1e-10):
        return False

    return True


# Is a dictionary a subset of another?
# https://stackoverflow.com/questions/9323749/python-check-if-one-dictionary-is-a-subset-of-another-larger-dictionary
def shells_are_subset(subset, superset):
    # For lists
    for item1 in subset:
        found = False
        for item2 in superset:
            if compare_shell(item1, item2):
                found = True
                break
        if not found:
            return False

    return True


# What to replace with
source_file = sys.argv[1]

# All JSON file to search for replacements
json_files = sys.argv[2:]

component_files = []
element_files = glob.glob("*.element.json")

for x in json_files:
    if x == source_file:
        continue
    else:
        component_files.append(x)

# Read in the source file
sdata = bse.read_json_by_path(source_file)
sname = os.path.splitext(source_file)[0]
selements = sdata['basisSetElements']

# Map of what we replaced or added
replaced_map = {}
added_map = {}

for cfile in component_files:
    #print("Comparing with {}".format(cfile))
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

        elif shells_are_subset(sel['elementElectronShells'], cel['elementElectronShells']):
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
        bse.write_json_basis(cfile, cdata)

# print out the replacement map
for k, v in replaced_map.items():
    print("Replaced in {}: {}".format(k, v))
for k, v in added_map.items():
    print("Partially replaced in {}: {}".format(k, v))

# Now go through all the atom basis files, doing replacements
for afile in element_files:
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
        bse.write_json_basis(afile, adata)
