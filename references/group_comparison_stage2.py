"""
Garbage and convoluted code attempting to parse the formless REF data using web of science.
"""

import glob
import difflib
import json
import collections

# Pull in globals and make temps
with open("parse_data/journal_abbv.txt", "r") as infile:
    journal_abbv = infile.read().splitlines()

authors_dict = {}
authors_count = collections.defaultdict(int)
author_translators = {
    "Kirk A. Peterson": "K. A. Peterson", 
    "P. von R. Schleyer": "P. R. Schleyer",
    "P. v. R. Schleyer": "P. R. Schleyer",
    "P. V. R. Schleyer": "P. R. Schleyer",

    "James A. Platts": "J. A. Platts",

    "George A. Petersson": "G. A. Petersson",

    "J-P. Blandeau": "J-P. Blaudeau",

    "T. v. Mourik": "T. van Mourik",

    "O. Roos": "B. O. Roos",
    ". O. Roos": "B. O. Roos",

    "B come from J. D. Dill": "J. D. Dill",

    "Larry A. Curtiss": "L. A. Curtiss",
    "J. Grant Hill": "J. G. Hill",

   "Duminda S. Ranasinghe": "D. Ranasinghe",

    # Valid!
    #['G. A. Petersson', 'K. A. Peterson']
    #['J. Lehtola', 'S. Lehtola']

}

errors = []
total_cit = 0

journals_dict = {}
journals_count = collections.defaultdict(int)
journal_translators = {
    "J. Phys. Chem. A.": "J. Phys. Chem. A",
    "J. Chem. Theo. Comp.": "J. Chem. Theory Comput.",
    "J. Chem. Theory Comp.": "J. Chem. Theory Comput.",
    "J. Chem. Theory Comput": "J. Chem. Theory Comput.",
    "Comput. Theor. Chem.": "Compt. Theor. Chem.",
    "J. Am. Chem. Soc.": "J. Am. Chem. Soc",
    "Theoret. Chimica Acta": "Theor. Chim. Acta",
    "J. Comp. Chem.": "J. Comput. Chem.",
    "J. Chem. Phys": "J. Chem. Phys.",
    "Journal of Molecular Modeling": "J. Mol. Model.",
    "J.Chem.Phys.": "J. Chem. Phys.",

    # Shrnink abbvs
    "The Journal of Chemical Physics": "J. Chem. Phys.",
    "The Journal of chemical physics": "J. Chem. Phys.",
    "Journal of Chemical Theory and Computation": "J. Chem. Theory Comput.",
    "Journal of Computational Chemistry": "J. Comput. Chem.",
    "Journal of Physical Chemistry A": "J. Phys. Chem. A",
    "Chemical Physics Letters": "Chem. Phys. Lett.",
    "Chem. Phys. Letters": "Chem. Phys. Lett.",
    "Molecular Physics": "Mol. Phys.",
    "Physical Chemistry Chemical Physics": "Phys. Chem. Chem. Phys.",
    "Theoretical Chemistry Accounts": "Theor. Chem. Acc.",
    "J. Mol. Struct. (Theochem)": "J. Mol. Struct. THEOCHEM",
    "J. Mol. Struct. (THEOCHEM)": "J. Mol. Struct. THEOCHEM",
    "Journal of Molecular Structure: THEOCHEM": "J. Mol. Struct. THEOCHEM",
    "Journal of Chemical Physics": " J. Chem. Phys.",
    "Theoretica Chimica Acta": "Theor. Chim. Acta",
}

#def build_author_compare

results = {}
for infile in glob.glob("stage1/*.json"):
    total_cit += 1
    with open(infile, "r") as infile_data:
        data = json.load(infile_data)

    if data["valid"] is False:
        errors.append(infile)
        continue

    found_all = True
    parsed_citations = []
    for cit in data["citations"]:
        if cit["valid"] is False:
            found_all = False
            continue

        # Handle journal
        j = cit["journal"]
        if j is False:
            found_all = False
            cit["valid"] = False
            continue

        j = j.strip()

        if len(j) == 0:
            cit["valid"] = False
            cit["journal"] = False
            found_all = False
            continue

        # People cannot spell!
        if j in journal_translators:
            j = journal_translators[j]

        j_list = difflib.get_close_matches(j, journal_abbv, cutoff=0.95)
        if len(j_list) == 1:
            j = j_list[0]
            if j in journals_dict:
                journals_dict[j] |= set([j])
            else:
                journals_dict[j] = set([j])
        elif len(j_list) == 0:
            continue
            print("Journal: Warning cannot find %s" % j)
        else:
            print("Journal: Found matches %s : %s" % (j, ", ".join(j_list)))
            continue

        cit["journal"] = j
        journals_count[j] += 1


        # Handle authors
        new_authors = []
        if len(cit["authors"]) == 0:
            found_all = False
            continue

        for author in cit["authors"]:
            author = author.strip()
            author = ". ".join(x.strip() for x in author.split("."))

            if ("Note:" in author) or (len(author) > 40):
                new_authors.append(False)
                continue
                

            if author in author_translators:
                author = author_translators[author]
    
            author_list = difflib.get_close_matches(author, list(authors_dict), cutoff=0.95)
            if len(author_list) == 0:
                authors_dict[author] = set([author])
            elif len(author_list) == 1:
                author = author_list[0]
                authors_dict[author_list[0]] |= set([author])
            else:
                print("Multiple authors found %s | %s" % (author, ", ".join(author_list))) 
            journals_count[j] += 1
   
            authors_count[author] += 1 
            new_authors.append(author)
#            print(author, author_list)

        cit["authors"] = new_authors

        
        parsed_citations.append(cit)

    if found_all:
        results[infile] = data

        

for k, v in journals_dict.items():
    if len(v) > 1:
        print("%30s : %s" % (k, ", ".join(v)))
        raise Exception("Duplicate journal name found and not parsed")

if False:
    print("Journals %d: " % len(journals_count))
    for key in sorted(journals_count):
        print("%4d | %s" % (journals_count[key], key))
    
    print("Authors %d: " % len(authors_count))
    for key in sorted(authors_count):
        print("%4d | %s" % (authors_count[key], key))

articles_dict = {}
articles_found = 0
results_parsed = 0

keyends = "abcdefghijkl"


# Find duplicates 
for name, data in results.items():

    if len(data["citations"]) == 0:
        continue

    complete = True
    new_citations = []
    for cit in data["citations"]:
        if (len(cit["authors"]) == 0) or (False in cit["authors"]):
            complete = False
            break

        fkey = cit["authors"][0].split()[-1].lower()
        fkey += ":" + str(cit["year"])

        possible_matches = [x for x in articles_dict.keys() if x.startswith(fkey)] 
        if len(possible_matches) == 0:
            key = fkey + keyends[0]
            articles_dict[key] = cit 
            new_citations.append({"article": key, "Z": cit["Z"], "original": cit["original"]})
            continue
        else:
            found_match = False
            for pmatch in possible_matches:
                match_art = articles_dict[pmatch]
                if cit["journal"] != match_art["journal"]:
                    continue
                if cit["page"] != match_art["page"]:
                    continue
                if cit["volume"] != match_art["volume"]:
                    continue
                if set(cit["authors"]) != set(match_art["authors"]):
                    continue

                new_citations.append({"article": pmatch, "Z": cit["Z"], "original": cit["original"]})
                found_match = True
                break

            if found_match is False:
                key = fkey + keyends[len(possible_matches)]
                new_citations.append({"article": key, "Z": cit["Z"], "original": cit["original"]})
                articles_dict[key] = cit 
                

        articles_found += 1

    #if len(data["citations"]) == len(
    if complete:
        print(len(data["citations"]))
        data["citations"] = new_citations
        results_parsed += 1
        with open("stage2/" + name.split('/')[-1], "w") as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)

with open("REFERENCES.json", "w") as outfile:
    json.dump(articles_dict, outfile, indent=4, sort_keys=True)

            
print("Total number of basis sets %d" % total_cit)
print("Total number of basis sets parsed %d" % len(results))
print("Total number of basis set articles parsed %d" % results_parsed)
print("Total number of articles found %d" % articles_found)
print("Total number of unique articles found %d" % len(articles_dict))




