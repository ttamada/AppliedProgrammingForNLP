#!/usr/bin/env python
__author__ = 'tetsuhiro'

from collections import Counter
from nltk.tokenize import word_tokenize
import argparse
from nltk.corpus import stopwords

parser = argparse.ArgumentParser(description="Create frequency list.")
parser.add_argument("filename", help="file which a frequency list should be created from")
parser.add_argument("-f", "--filter", action="store_true", help="filter stopwords")
parser.add_argument("-t","--top", nargs="?", const=1, type=int, help="return only top n words (default 1)")
parser.add_argument("--min-freq", nargs="?", const=0, type=int, help="cut off words below a certain frequency")
args = parser.parse_args()

with open(args.filename) as f:
    text = f.read().decode('utf-8') # nltk needs decoded string
tokens = word_tokenize(text) # TODO: replace with more performant tokenization method
if args.filter:
    tokens = [t for t in tokens if t not in stopwords.words("english")]

# tokens = [t for t in tokens if t not in string.punctuation]
freqDict = Counter([t.encode('utf-8') for t in tokens]) # encode back to utf-8 so piping this script works

#show top n tokens as option
top_words = len(freqDict)
if args.top > 0:
    top_words = args.top

min_freq = 0
if args.min_freq > 0:
    min_freq = args.min_freq

for tup in freqDict.most_common(top_words):
        if tup[1] >= min_freq:
            print '{:20}{}'.format(*tup)


"""
# second argument specifies how many of the most frequent words should be printed
# by default, all words are printed
try:
    top_words = int(sys.argv[2])
except IndexError:
    top_words = len(freqDict) # no number was set, we will use all then

for tup in freqDict.most_common(top_words):
    # simpler tabbing than with str.ljust
    print '{:20}{}'.format(*tup)
"""
