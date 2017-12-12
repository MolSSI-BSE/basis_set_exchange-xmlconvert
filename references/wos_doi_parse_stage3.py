"""
Garbage and convoluted code attempting to parse the formless REF data using web of science.
"""

import glob
import difflib
import json
from wos import WosClient
import wos.utils
from xmljson import badgerfish as bf

refs = {}
errors = 0
total_cit = 0

with WosClient() as client:
    for infile in glob.glob("stage1/*.json"):
        total_cit += 1
        with open(infile, "r") as infile_data:
            data = json.load(infile_data)
    
        if data["valid"] is False:
            continue
    
        all_Z = set()
        all_found = True
        for cit in data["citations"]:
            if cit["valid"] is False:
                all_found = False
                break
    
            # Parse cit
            wos_query = ""
            if cit["authors"]:
                wos_query += 'AU="'
                for num, aut in enumerate(cit["authors"]):
                    if num >= 1:
                        wos_query += " AND "
                    tmp = aut.split()

                    # Last, First Initial
                    author = tmp[-1] + ", " + " ".join(tmp[:-1]) 
                    print(author)
                    wos_query += author
                wos_query += '"'
    
            if cit["year"]:
                wos_query += ' AND PY="%d"' % cit["year"]
    
            if cit["title"]:
                wos_query += ' AND TI="%s"' % cit["title"].replace(" and ", "")
  
            wos_query = wos_query.encode("UTF-8") 
            print(wos_query) 
            raise Exception()
            data = wos.utils.query(client, wos_query)
            print(data)
            data = bf.data(data)
            print(data)
            raise Exception()
