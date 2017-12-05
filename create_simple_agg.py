#!/usr/bin/env python3

import argparse
import bse_xml 

parser = argparse.ArgumentParser()
parser.add_argument('xmlfile', help='XML file to convert', type=str)
args = parser.parse_args()

bse_xml.create_xml_agg(args.xmlfile)
