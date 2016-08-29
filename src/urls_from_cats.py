#!/usr/bin/env python

from lxml import etree
from sys import argv
from os.path import getmtime
from datetime import datetime

# initialize root element of output xml
NAMESPACES = {None: 'http://www.w3schools.com',
              'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
location_attribute = '{%s}noNamespaceSchemaLocation' % 'http://www.w3.org/2001/XMLSchema-instance'
root = etree.Element('urls', nsmap=NAMESPACES, attrib={location_attribute: 'urls.xsd'})

# get modification date of input file
mod_time = datetime.fromtimestamp(getmtime(argv[1]))
mod_date = '{0:04d}-{1:02d}-{2:02d}'.format(mod_time.year, mod_time.month, mod_time.day)
# parse input file
xml_in = etree.parse(argv[1])

# find cat elements ignoring namespaces, since we should only encounter one
# create appropriate url elements while doing so
id_str = 'faz_'
id_cat = 1
for cat_elem in xml_in.findall('//{*}cat'):
    #TODO: not url of category but url of articles of that category
    #need to access faz online
    url_elem = etree.SubElement(root, 'url', {'id': id_str + '{0:02d}'.format(id_cat),
                                              'domain': cat_elem.attrib['domain'],
                                              'cat': cat_elem.attrib['name'],
                                              'subcat': '',
                                              'date': mod_date})

    url_elem.text = cat_elem.attrib['url']
    # go through subcat elements, ignore name spaces again ;)
    # optional todo: write function to extract this from the elements, since almost the same for top elements
    id_sub = 1
    for subcat_elem in cat_elem.findall('{*}subcat'):
        #TODO: not url of subcategory but url of articles of that category
        #need to access faz online
        url_elem_sub = etree.SubElement(root, 'url', {'id': id_str + '{0:02d}'.format(id_cat) + '_' + '{0:02d}'.format(id_sub),
                                              'domain': cat_elem.attrib['domain'],
                                              'cat': cat_elem.attrib['name'],
                                              'subcat': subcat_elem.attrib['name'],
                                              'date': mod_date})

        url_elem_sub.text = subcat_elem.attrib['url']
        id_sub += 1


    id_cat += 1

print etree.tostring(root, pretty_print=True)
