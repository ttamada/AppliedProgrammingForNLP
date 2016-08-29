#!/usr/bin/env python

from lxml import etree
from os.path import getmtime
from datetime import datetime
from lxml.html import parse
import argparse

parser = argparse.ArgumentParser(description="Scrape each category site from faz.net to retrieve a set of article links.")
parser.add_argument("filename", help="Category file which article links are extracted from")
parser.add_argument("-a", "--all", action="store_true", help="Extract all article links(default: only from the first page)")
args = parser.parse_args()

# initialize root element of output xml
NAMESPACES = {None: 'http://www.w3schools.com',
              'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
location_attribute = '{%s}noNamespaceSchemaLocation' % 'http://www.w3.org/2001/XMLSchema-instance'
root = etree.Element('urls', nsmap=NAMESPACES, attrib={location_attribute: 'urls.xsd'})

# get modification date of input file
mod_time = datetime.fromtimestamp(getmtime(args.filename))
mod_date = '{0:04d}-{1:02d}-{2:02d}'.format(mod_time.year, mod_time.month, mod_time.day)
# parse input file
xml_in = etree.parse(args.filename)

# find cat elements ignoring namespaces, since we should only encounter one
# create appropriate url elements while doing so
id_str = 'faz_'
id_cat = 1
for cat_elem in xml_in.findall('//{*}cat'):
    id_sub = 1
    for subcat_elem in cat_elem.findall('{*}subcat'):
        #need to access faz online
        if args.all:
            #there are multiple pages of article lists for a subcategory in faz.net
            #for the argument option -a, the number of pages of article lists is counted
            subcat_tree = parse(subcat_elem.attrib['url'])
            pages = [int(page) for page in subcat_tree.xpath('//div[@class="Rubrikenkopf"]//div[@class="PagerNav right"]//a[@onclick="new_tag_wrapper();"]/text()')]
            if pages != []:
                numberOfPages = max(pages)
            else:
                numberOfPages = 1
        else:
            numberOfPages = 1
        for page in range(1,numberOfPages+1):
            if page == 1:
                try:
                    article_tree = parse(subcat_elem.attrib['url'])
                except:
                    pass
            else:
                try:
                    article_tree = parse(subcat_elem.attrib['url']+"s"+str(page)+".html")
                except:
                    pass
            try:
                article_links = [a.attrib.get('href') for a in article_tree.xpath('//a[@class="TeaserHeadLink"]') if a.attrib.get('href').startswith('/')]
                id_art = 1
                for article_link in article_links:
                    url_elem_sub = etree.SubElement(root, 'url', {'id': id_str + '{0:02d}'.format(id_cat) + '_' + '{0:02d}'.format(id_sub) + '_' + '{0:02d}'.format(id_art),
                                                          'domain': cat_elem.attrib['domain'],
                                                          'cat': cat_elem.attrib['name'],
                                                          'subcat': subcat_elem.attrib['name'],
                                                          'date': mod_date,
                                                          'title': "" })
                    url_elem_sub.text = "http://www.faz.net"+article_link
                    id_art += 1
            except:
                pass
        id_sub += 1
    id_cat += 1

print etree.tostring(root, pretty_print=True)
