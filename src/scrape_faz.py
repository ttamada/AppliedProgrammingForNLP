#!/usr/bin/env python

from lxml.html import fromstring
from lxml import etree
from sys import argv
import time
import os
import requests
import codecs

# parse input file
xml_in = etree.parse(argv[1])

# create output directory if necessary
out_dir = os.path.join('res', 'faz')
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

# set whether to wait a few seconds after each time hitting an online page
slow = True

# def get_article_link(cat_url):
#    '''
#    try to get the link to the first article of a category
#    this whole thing is a bit nasty, but so is faz.net
#    '''
#    cat_page = fromstring(requests.get(cat_url).text)
#    if slow:
#        time.sleep(5)
#    # get all internal (starting with "/") a elements of class TeaserHeadLink
#    article_links = [a.attrib.get('href') for a in cat_page.xpath('//a[@class="TeaserHeadLink"]') if a.attrib.get('href').startswith('/')]
#    if article_links:
#        # return first link and prefix with faz.net
#        return 'http://www.faz.net/' + article_links[0]
#    else:
#        return None

def parse_html(an_article_link):
    '''
    try to assemble some text from a faz article page
    will return empty string if the standard elements were not found
    '''
    
    # we might run into articles spanning several pages, fortunately FAZ offers the button "Artikel auf einer Seite"
    # this links to a java script function which does nothing more than that:
    if '#' in an_article_link:
        an_article_link = an_article_link[:an_article_link.index('#')]
    an_article_link += '?printPagedArticle=true'
    
    html_doc = fromstring(requests.get(an_article_link).text)
    
    # TODO: one could also think about incorporating text in <title> tag...
    
    # xpath function always returns list, but id element is unique so accessing with [0] is unproblematic
    intro_elems = html_doc.xpath('//div[@id="artikelEinleitung"]')

    if intro_elems:
        intro_elem = intro_elems[0]

        title = ' - '.join([t.strip() for t in intro_elem.xpath('./h2')[0].itertext() if t.strip()])

        summary = intro_elem.xpath('./p')[0].text.strip()

        intro = title + '\n\n' + summary
    else:
        intro = ''

    # (currently) there will be two divs matching this expression. however
    text_elems = html_doc.xpath('//div[@class="FAZArtikelText"]')

    if text_elems:
        text_elem = text_elems[0]

        # now lets assemble the relevant text:
        text = ''

        for elem in text_elem.iter():
            # the only two html tags we're interested in
            if elem.tag == 'h2' or elem.tag == 'p':
                if elem.text:
                    if not 'class' in elem.attrib or elem.attrib.get('class') == 'First PreviewPagemarker':
                        text += elem.text.strip() + '\n'
                #for paragraphs with text links
                elif elem.getchildren() != []:
                    text += ''.join(elem.itertext())

    else:
        text = ''

    if intro or text:
        return intro + '\n\n' + text.strip()
    else:
        return ''
    
# now finally the programs procedure
cat_pages = []
url_elems = xml_in.findall('//{*}url')
num_urls = len(url_elems)
for i, url_elem in enumerate(url_elems):

    cat = url_elem.attrib['cat']
    subcat = url_elem.attrib['subcat']
    art_id = url_elem.attrib['id']

    article_link = url_elem.text
    print 'processing article', str(i+1) + '/' + str(num_urls) + ':', article_link

    if article_link:
        text_out = parse_html(article_link)
        if slow:
            time.sleep(5)

        if text_out:
            # write to outputfile
            with codecs.open(os.path.join(out_dir, art_id + '.txt'), 'w', 'utf-8') as f:
                f.write(text_out)
        else:
            print 'Could not find text for', url_elem.text, '-- No output generated for id', art_id

    else:
        # these are the changes on the page already mentioned...
        print 'Could not find article for', url_elem.txt, ' -- No output generated for id', art_id

