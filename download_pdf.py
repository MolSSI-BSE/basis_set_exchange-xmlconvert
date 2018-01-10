
import json
import os
import sys
import glob
import time
import requests
import subprocess

import bse


def get_pdf(doi, outfile):

    if os.path.isfile(outfile):
        print("Output file '{}' exists".format(outfile))
        return

    # Requested by crossref API
    headers = {
        'User-Agent': 'BSEConverter 1.0 (mailto:bpp4@vt.edu)'
    }

    r = requests.get('https://api.crossref.org/works/'+doi, headers=headers)
    if r.status_code != 200:
        print("Crossref returned {}".format(r.status_code))
    else:
        j = json.loads(r.text)
        r1 = j['message']
        
        pdf_url = None
        page_url = None

        if 'URL' in r1:
            page_url = r1['URL']

        if 'link' in r1:
            r1 = r1['link'][0]

            if 'URL' in r1:
                pdf_url = r1['URL']

                # Springer link seems to have bad URLs
                if 'springerlink' in pdf_url:
                    pdf_url = "https://link.springer.com/content/pdf/{}.pdf".format(doi)
                # Same with wiley
                if 'api.wiley.com' in pdf_url:
                    print("Wiley sucks. You are on your own. DOI: {}".format(doi))
                    return 

                print(pdf_url)
                 
                resp = requests.get(pdf_url, headers=headers)

                if resp.status_code != 200:
                    print("--!!! ERROR: Returned {}".format(resp.status_code))
                    return

                with open(outfile, 'wb') as f:
                    f.write(resp.content)

            else:
                if page_url:
                    print("No link found. Manually go to {}".format(page_url))
                else:
                    print("No link found. You are on your own")

reffile = sys.argv[1]
with open(reffile, 'r') as f:
    refdata = json.loads(f.read())

for k,v in refdata.items():
    if "DOI" in v and v["DOI"] != "":
        filename = k.replace(':', '') + ".pdf"
        filename = os.path.join('pdf', filename)
        if not os.path.isfile(filename):
            #print('-'*80)
            print("{} {}".format(v['DOI'], filename))
            subprocess.call(["firefox", "https://dx.doi.org/{}".format(v["DOI"])])
            #get_pdf(v['DOI'],filename)
