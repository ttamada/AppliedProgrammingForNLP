#!/usr/bin/env python

from lxml.html import parse
from lxml import etree

# initialize root element of output xml
NAMESPACES = {None: 'http://www.w3schools.com',
              'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
location_attribute = '{%s}noNamespaceSchemaLocation' % 'http://www.w3.org/2001/XMLSchema-instance'
root = etree.Element('cats', nsmap=NAMESPACES, attrib={location_attribute: 'cats.xsd'})

# parse faz.net
faz_html = parse('http://www.faz.net')

# get nav element
# xpath returns list, but since we're searching for id, only one will be found
nav = faz_html.xpath('//ul[@id="nav"]')[0]

# function to get the name of a category and the corresponding link from the 'li' element as it is extracted from faz.net
def dict_from_li_elem(li_elem, domain=''):
    a_elt = li_elem.find('a')
    if domain:
        return {'name': a_elt.text, 'url': a_elt.attrib['href'], 'domain': domain}
    return {'name': a_elt.text, 'url': a_elt.attrib['href']}

# go through (grand)children of nav (li elements)
# create SubElements with text = \n to make output a bit more readable
for cat_elt in nav.getchildren():
    cat = etree.SubElement(root, 'cat', dict_from_li_elem(cat_elt, domain='http://www.faz.net'))
    for subcat_elt in cat_elt.find('ul').getchildren():
        etree.SubElement(cat, 'subcat', dict_from_li_elem(subcat_elt))

# TODO: adjust output as needed
print etree.tostring(root, pretty_print=True)
