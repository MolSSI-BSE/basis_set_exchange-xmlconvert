import sys
import requests
import json

def query_crossref(query):
    # Requested by crossref API
    headers = {
        'User-Agent': 'BSEConverter 1.0 (mailto:bpp4@vt.edu)'
    }

    r = requests.get('https://api.crossref.org/works/' + str(query), headers=headers)
    #r = requests.get('https://api.crossref.org/works', params={'query': query}, headers=headers)
    if r.status_code != 200:
        return None
    else:
        j = json.loads(r.text)["message"]
        #return j['message']['items'][0]
        return j

testquery = sys.argv[1]
result = query_crossref(testquery)

print("Query: ", testquery)
print("First result:")
print(': '.join(result['title'])) # Title is a list?
print('Authors: ')
for a in result['author']:
    print('    {}, {}'.format(a['family'], a['given']))
print('{}, v{}, pp {}'.format(result['container-title'][0], result['volume'], result['page']))
print("DOI: ", result['DOI'])

print(" ")
del result["reference"]
print(json.dumps(result, indent=4))
