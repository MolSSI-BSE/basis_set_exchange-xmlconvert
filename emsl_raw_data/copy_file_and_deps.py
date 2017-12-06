#!/usr/bin/env python3

import sys
import os
import shutil
import xml.etree.ElementTree as ET

# XML Namespaces
ns = { 'default': 'http://purl.oclc.org/NET/EMSL/BSE',
       'cml': 'http://www.xml-cml.org/schema/cml2/core',
       'dc': 'http://purl.org/dc/elements/1.1/',
       'dct': 'http://purl.org/dc/terms/',
       'xlink': 'http://www.w3.org/1999/xlink'
}


def get_links(node, tag):
    all_nodes = node.findall(tag, ns)
    if not all_nodes:
        return None
    ret = []
    for a in all_nodes:
        ret.append(a.attrib['{{{}}}href'.format(ns['xlink'])])

    return ret


def get_single_link(node, tag):
    l = get_links(node, tag)
    if l:
        return l[0]
    else:
        return None

def copy_xml_file(filepath, destdir):
    srcdir = os.path.dirname(filepath)
    basename = os.path.splitext(filepath)[0]

    # Parse the XML
    root = ET.parse(filepath).getroot()

    print("Copying {} to {}".format(filepath, destdir))
    shutil.copy(filepath, destdir)

    # Copy the reference
    reffile = get_single_link(root, 'default:referencesLink')
    if reffile:
        reffile = os.path.join(srcdir, reffile)
        print("Copying {} to {}".format(reffile, destdir))
        shutil.copy(reffile, destdir)

    # Is this an AGG file? If so, copy the dependencies
    other_xml = []

    links = get_single_link(root, 'default:primaryBasisSetLink')
    if links:
        other_xml.append(links)

    links = get_links(root, 'default:basisSetLink')
    if links:
        other_xml.extend(links)

    for f in other_xml:
        copy_xml_file(os.path.join(srcdir, f), destdir) 

copy_xml_file(sys.argv[1], sys.argv[2])

