import copy

valid_journals = [
    "Can. J. Chem.", "Chem. Phys. Lett.", "Comput. Theor. Chem.", "J. Am. Chem. Soc.",
    "J. Chem. Phys.", "J. Chem. Theory Comput.", "J. Comput. Chem.", "J. Mol. Model.",
    "J. Mol. Struct. THEOCHEM", "J. Phys. B", "J. Phys. Chem.", "J. Phys. Chem. A",
    "Magn. Res. Chem.", "Mol. Phys.", "Phys. Chem. Chem. Phys.", "Theor. Chem. Acc.",
    "Theor. Chim. Acta", "Int. J. Quant. Chem.", "Collec. Czech. Chem. Commun.",
    "Inorg. Chem.", "TURBOMOLE basis set library", "J. Phys. B"
]

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
    "Theoretical Chemistry Accounts: Theory, Computation, and Modeling (Theoretica Chimica Acta)": "Theor. Chim. Acta",
    "Canadian Journal of Chemistry" : "Can. J. Chem.",
    "Inorganic Chemistry": "Inorg. Chem.",
    "Collection of Czechoslovak Chemical Communications": "Collec. Czech. Chem. Commun.",
    "Journal of the American Chemical Society": "J. Am. Chem. Soc.",
    "The Journal of Physical Chemistry A": "J. Phys. Chem. A",
    "The Journal of Physical Chemistry": "J. Phys. Chem.",
    "Computational and Theoretical Chemistry": "Comput. Theor. Chem.",
    "International Journal of Quantum Chemistry": "Int. J. Quant. Chem.",
    "Chemical Physics": "J. Chem. Phys.",
    "Journal of Physics B: Atomic and Molecular Physics": 'J. Phys. B'
}

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
    "Trygve Helgaker": "T. Helgaker",
    "Frank Jensen": "F. Jensen",
    "C. W. Bauschlicher": "C. W. Bauschlicher, Jr.",
    "Dmitrij Rappoport": "D. Rappoport",
    "F. Furche": "F. Furche",
    "Christof Hattig": "C. Hattig",
    "Valera Veryazov": "V. Veryazov",
    "Vitaly Rassolov" : "Vitaly A. Rassolov",
    "W. C. ERMLER" : "Walter C. Ermler",
    "W. C. Ermler": "Walter C. Ermler", 
    "Thom H. Dunning": "T. H. Dunning",
    "T. H. DUNNING": "T. H. Dunning",
    "R. B. ROSS": "R. B. Ross",
    "Per-�ke Malmqvist" : "Per-Åke Malmqvist",
    "Heinzwerner Preuß" : "Heinzwerner Preuss",
    "H. Preu�" : "Heinzwerner Preuss",

    # Valid!
    #['G. A. Petersson', 'K. A. Peterson']
    #['J. Lehtola', 'S. Lehtola']
}


known_journals = valid_journals + list(journal_translators)
known_authors = list(author_translators)

# Lookup dictionaries
_temp_symbol = [
    "X", "H", "HE", "LI", "BE", "B", "C", "N", "O", "F", "NE", "NA", "MG", "AL", "SI", "P", "S",
    "CL", "AR", "K", "CA", "SC", "TI", "V", "CR", "MN", "FE", "CO", "NI", "CU", "ZN", "GA", "GE",
    "AS", "SE", "BR", "KR", "RB", "SR", "Y", "ZR", "NB", "MO", "TC", "RU", "RH", "PD", "AG", "CD",
    "IN", "SN", "SB", "TE", "I", "XE", "CS", "BA", "LA", "CE", "PR", "ND", "PM", "SM", "EU", "GD",
    "TB", "DY", "HO", "ER", "TM", "YB", "LU", "HF", "TA", "W", "RE", "OS", "IR", "PT", "AU", "HG",
    "TL", "PB", "BI", "PO", "AT", "RN", "FR", "RA", "AC", "TH", "PA", "U", "NP", "PU", "AM", "CM",
    "BK", "CF", "ES", "FM", "MD", "NO", "LR", "RF", "DB", "SG", "BH", "HS", "MT", "DS", "RG", "UUB",
    "UUT", "UUQ", "UUP", "UUH", "UUS", "UUO"
]

atom_number_to_symbol = {k: v for k, v in zip(range(len(_temp_symbol)), _temp_symbol)}
atom_number_to_symbol[-1] = "NOTE"

atom_symbol_to_number = {k: v for v, k in atom_number_to_symbol.items()}


