
import json
import os
import sys
import glob
import time
import requests

import bse

reffile = sys.argv[1]

with open(reffile, 'r') as f:
    refdata = json.loads(f.read())

for k,v in refdata.items():
    if 'year' in v:
        y = v['year']
        ystr = ":" + str(y)

        if not ystr in k:
            print("{}  year = {}".format(k, y))
    else:
        print("{} DOES NOT HAVE A YEAR")

#bse.write_references(reffile, refdata)
