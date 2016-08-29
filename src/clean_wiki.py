#!/usr/bin/python

import sys
import re
import string

# parse filename from argument
filename = sys.argv[1]

# read file
with open(filename) as f:
    xml = f.read()
        
# to parse xml more nicely use for example lxml
# get everything between <text> tags
texts = re.findall(r'<text.*?>(.*?)</text>', xml, re.DOTALL)
        
# get rid of some byproducts
texts = [t for t in texts if not t.upper().startswith('#REDIRECT')]
        
#TODO remove header? links and other markup stuff
        
#remove html tags like &lt; and replace by space
texts = [re.sub(r'&.+?;', ' ', t) for t in texts]
        
#strip all punctuation
#TODO: find more sophisticated way which preserves correct punctuation
for final_text in [t.translate(None, string.punctuation) for t in texts]:
    print final_text
