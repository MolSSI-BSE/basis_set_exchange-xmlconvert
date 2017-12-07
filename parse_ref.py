import glob
import xml
import difflib
import xml.etree.ElementTree as ET

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
    root = ET.parse(infile).getroot()
    data = root.findall("default:notes", {"default": "http://purl.oclc.org/NET/EMSL/BSE"})[0].text
    print(data)
    print("----------\n")
    data = data.splitlines()

    ret = []

    inside_refs = False

    for line in data:
        if ":" in line:
            inside_refs = True
            tmp = line.split(":")
            if len(tmp) != 2:
                raise ValueError("Citation list must have only two elements on each side of ':'\n"
                                 "    Found: %s" % line) 
            ret.append((tmp[0].strip(), tmp[1].strip()))
        # Multiline ref
        elif inside_refs:
            ret[-1] = (ret[-1][0], ret[-1][1] + " " + line)
    return ret

def _parse_citation(atoms, citation):
    print('\n=====')
    print(atoms)
    print(citation)
    ret = {}        
    
    ### Parse atoms
    if "," in atoms:
        atoms = [x.strip() for x in atoms.split(",")]
    elif " " in atoms:
        atoms = atoms.split(" ")
    else:
        atoms = [atoms]

    ret["Z"] = []
    for at in atoms:
        if "-" in at:
            start, stop = at.split("-")
            start = atom_symbol_to_number[start.strip().upper()]
            stop = atom_symbol_to_number[stop.strip().upper()]

            ret["Z"].extend(list(range(start, stop + 1)))
        else:
            ret["Z"].append(atom_symbol_to_number[at.strip().upper()])
    ret["Z"].sort()
        
    ### Parse citation

    # First split out author names
    # Hack our Jr's
    citation = citation.replace(" Jr.", "")
    and_line = citation.find("and")

    # Single author
    if (and_line == -1):
        # Find first comma to delineate author/article
        fc = citation.find(",")
        authors = [citation[:fc]]
        citation = citation[fc:].strip()

    # Multi author
    else:
        # Find first comma after and to delineate author/article
        fc = and_line + citation[and_line:].find(",")
        citation = citation.replace(",and", ",")
        citation = citation.replace("and", ",")

        # Parse authors
        authors = citation[:fc].split(",")
        authors = [x.strip().replace(",", "") for x in authors if (len(x.strip()) and len(x) < 40)]

        citation = citation[fc:].strip()

    if citation.startswith(", "):
        citation = citation[2:]

    # Set authors
    ret["authors"] = authors

    # Try to geuss Y/P/V
    ypv_citation = citation.split()
    ret["year"] = is_number(string_remove_chars("().,", ypv_citation[-1]))
    ret["page"] = is_number(string_remove_chars("().,", ypv_citation[-2]))
    ret["volume"] = is_number(string_remove_chars("().,", ypv_citation[-3]))

    ypv_left = len(" ".join(ypv_citation[-3:]))

    # Journal/Title
    ret["journal"] = [x for x in citation[:-ypv_left].split(",") if len(x.strip())][-1]
 
   
    print('------') 
    for k, v in ret.items():
        print("%10s : %s" % (k, v))
    print('------') 

def parse_ref_file(infile):

    # Parse
    citations = []
    for atoms, cit in _read_file(infile):
        json_cit = _parse_citation(atoms, cit)
        citations.append(json_cit)


# Quick tests
#bfile = "data/xml/CC-PVDZ-BS-REF.xml"
bfile = "data/xml/CC-PVQZ-PP-BS-REF.xml"
blob = _read_file(bfile)
#assert len(blob) == 6
_parse_citation(*blob[0])
_parse_citation(*blob[1])
_parse_citation(*blob[2])
_parse_citation(*blob[3])


##http://purl.oclc.org/NET/EMSL/BSE'
#for infile in glob.glob("data/xml/CC*REF.xml"):
#
#    # Grab data
#    print("Basis: %s" % infile)
#    parse_ref_file(infile)
#    
#
#    raise Exception()
