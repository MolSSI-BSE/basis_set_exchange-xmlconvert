"""
Garbage and convoluted code attempting to parse the formless REF data using web of science.
"""

import glob
import difflib
from wos import WosClient
import wos.utils
from xmljson import badgerfish as bf
import json
from xml.etree import ElementTree as ET

DO_PRINT = False

# Lookup dictionaries
_temp_symbol = [
    "X", "H", "HE", "LI", "BE", "B", "C", "N", "O", "F", "NE", "NA", "MG", "AL", "SI", "P", "S", "CL", "AR", "K", "CA",
    "SC", "TI", "V", "CR", "MN", "FE", "CO", "NI", "CU", "ZN", "GA", "GE", "AS", "SE", "BR", "KR", "RB", "SR", "Y",
    "ZR", "NB", "MO", "TC", "RU", "RH", "PD", "AG", "CD", "IN", "SN", "SB", "TE", "I", "XE", "CS", "BA", "LA", "CE",
    "PR", "ND", "PM", "SM", "EU", "GD", "TB", "DY", "HO", "ER", "TM", "YB", "LU", "HF", "TA", "W", "RE", "OS", "IR",
    "PT", "AU", "HG", "TL", "PB", "BI", "PO", "AT", "RN", "FR", "RA", "AC", "TH", "PA", "U", "NP", "PU", "AM", "CM",
    "BK", "CF", "ES", "FM", "MD", "NO", "LR", "RF", "DB", "SG", "BH", "HS", "MT", "DS", "RG", "UUB", "UUT", "UUQ",
    "UUP", "UUH", "UUS", "UUO"
]

atom_number_to_symbol = {k: v for k, v in zip(range(108), _temp_symbol)}
atom_symbol_to_number = {k: v for v, k in atom_number_to_symbol.items()}

with open("parse_data/journal_abbv.txt", "r") as infile:
    journal_abbv = infile.read().splitlines()


def string_remove_chars(chars, string):
    for x in chars:
        string = string.replace(x, "")
    return string


def is_number(val):
    try:
        return int(val)
    except ValueError:
        return False


def _read_file(infile):
    """
    Pulls in the 'notes' line from the REF files and strips the citations into a single line
    """
    root = ET.parse(infile).getroot()
    data = root.findall("default:notes", {"default": "http://purl.oclc.org/NET/EMSL/BSE"})[0].text
    if DO_PRINT:
        print(data.strip())
        print("----------\n")
    data = data.splitlines()

    ret = []

    inside_refs = False

    for line in data:
        if "Original" in line: continue
        if "Recontraction" in line: continue
        if ":" in line:
            inside_refs = True
            tmp = line.split(":", 1)
            #if len(tmp) != 2:
            #    raise ValueError("Citation list must have only two elements on each side of ':'\n"
            #                     "    Found: %s" % line)
            ret.append((tmp[0].strip(), tmp[1].strip()))
        # Multiline ref
        elif inside_refs:
            ret[-1] = (ret[-1][0], ret[-1][1] + " " + line)
    return ret


def _handle_atoms(atoms):
    """
    Provides a Z list for the atom string
    >>> _handle_atom("He-Li")
    [2, 3]
    """
    if "," in atoms:
        atoms = [x.strip() for x in atoms.split(",")]
    elif " " in atoms and ("-" not in atoms):
        atoms = atoms.split(" ")
    else:
        atoms = [atoms.strip()]

    ret = []
    for at in atoms:
        if "-" in at:
            start, stop = at.split("-")
            start = atom_symbol_to_number[start.strip().upper()]
            stop = atom_symbol_to_number[stop.strip().upper()]

            ret.extend(list(range(start, stop + 1)))
        else:
            ret.append(atom_symbol_to_number[at.strip().upper()])
    ret.sort()
    return ret


def _handle_cit(citation):
    """
    Decomposes a citation string into a series of fields
    """
    DO_PRINT = False

    ret = {"orginal": citation, "valid": False}

    # Filter out incomplete
    if "to be published" in citation.lower():
        return ret

    if "submitted" in citation.lower():
        return ret

    if len(citation.strip()) < 5:
        return ret

    #print("CIT, %s" %citation)
    if DO_PRINT:
        print(citation)
    
    ### Try to find Y/P/V
    ypv_citation = citation.split()
    if len(ypv_citation) > 3:
        ret["year"] = is_number(string_remove_chars("().,", ypv_citation[-1]))
        ret["page"] = is_number(string_remove_chars("().,", ypv_citation[-2]))
        ret["volume"] = is_number(string_remove_chars("().,", ypv_citation[-3]))

    ypv_data = [ret[x] for x in ["year", "page", "volume"]]
    if False in ypv_data:
        raise KeyError("Could not find year/page/volume")
    
    citation = " ".join(ypv_citation[:-3])
    if DO_PRINT:
        print(1, citation)

    ### Yank out authors 

    # Hack our Jr's
    citation = citation.replace(" Jr.", "")
    authors = []
    break_next = False
    author_enumerate = citation.replace("and", ",  ").split(",")
    chars_used = 0
    for num, sp in enumerate(author_enumerate):
        sp_chars = len(sp) + 1 

        # Are we nothing?
        sp = sp.strip()
        if len(sp) == 0:
            chars_used += sp_chars
            continue

        # Watch cases
        isjournal = difflib.get_close_matches(sp, journal_abbv)
        if isjournal:
            break
    
        # If we hit a `and` we will be done next iteration
        if break_next:
            break

        if "and" in sp:
            break_next = True

        # Authors should have a "." in their name
        if ("." in sp) and (len(sp) < 80):
            chars_used += sp_chars
            authors.append(sp) 
        else:
            break

    # Cleanup authors
    authors = [string_remove_chars([")", "(", "and", ","], x).strip() for x in authors]

    ret["authors"] = authors

    citation = citation[chars_used:].strip()
    if DO_PRINT:
        print(citation)

    if citation.startswith(","):
        citation = citation[1:]
    citation = citation.replace("  ", " ")
    citation = citation.replace("  ", " ")
    citation = citation.strip()
    if DO_PRINT:
        print(2, citation)

    # Set authors
    ret["authors"] = authors

    # Split from the left by 1, then unpack, ugh
    remain = citation[::-1].split(",", 1)
    remain = [x[::-1].strip() for x in remain][::-1]
    if DO_PRINT:
        print(remain)

    # Journal/Title
    ret["journal"] = False
    ret["title"] = False
    if (len(remain) == 1) and ("J." in remain[0]):
        ret["journal"] = remain[0].strip()
        ret
    elif len(remain) >= 2:
        ret["journal"] = remain[-1].strip()
        ret["title"] = remain[0].strip()
    ret["valid"] = True
    return ret


def _parse_citation(atoms, cit):

    ret = _handle_cit(cit)
    ret["Z"] = _handle_atoms(atoms)
    if DO_PRINT:
        print('---------')
        print(cit)
        for k, v in ret.items():
            print("%10s : %s" % (k, v))
        print('---------')
    return ret

def wos_query_BAD(val):
    wos_query = "TO=%s" % string_remove_chars(["(", ")", "and", "or"], cit)
    data = wos.utils.query(client, wos_query)

    print(data)
    data = bf.data(data)
    print(data)
    raise Exception()
    return ret


def parse_ref_file(infile):
    # Parse
    citations = []
    for atoms, cit in _read_file(infile):
        json_cit = _parse_citation(atoms, cit)
        citations.append(json_cit)

    return citations


# Quick tests

failures = 0
success = 0
for infile in glob.glob("data/xml/CC*REF.xml"):

    # Grab data
    #print("\n============")
    #print("Basis: %s" % infile)
    #jsons = parse_ref_file(infile)
    #for j in jsons:
    #    j["host"] = infile.split("/")[-1].replace("-REF", "")
    try:
        jsons = parse_ref_file(infile)
        success += 1
    except:
        print("Failed: %s" % infile)

        failures += 1

print("Success %d, Failures %d,  Ratio %3.2f" % (success, failures, success/(failures + success)))
        

raise Exception()
