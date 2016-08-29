#! /usr/bin/env python

import numpy as np
import operator
import argparse
from fractions import Fraction

parser = argparse.ArgumentParser(description='k nearest neighbors for word embedings')
group = parser.add_mutually_exclusive_group(required=True)
# there is no way to make a mutually exclusive group with positional arguments
# therefore this will require -w or -v
group.add_argument('-w', '--word', metavar='WORD', nargs='*', type=str,
                    help='word to print the k nearest neighbors for(if multiple words given, sum of the word vectors')
group.add_argument('-v', '--vector', metavar='VECTOR DIMENSION', type=float, nargs=50,
                    help='a 50d vector to print the k nearest neighbors for')
parser.add_argument('-k', metavar='K', type=int, default=5,
                    help='number of neighbors to print')
# the user may chose which distance measure to use
parser.add_argument('-d', '--distance', metavar='DISTANCE MEASURE', type=str, choices=['euclidean', 'manhattan', 'minkowski'], default='euclidean',
                    help='the distance measure to use\n' +\
                          'options are: "euclidean", "manhattan","minkowski(default order 3)"')
parser.add_argument('-p', metavar='MINKOWSKI DISTANCE ORDER', type=int,
                    help='minkowski distance order p')

args = parser.parse_args()

if args.p and args.distance != 'minkowski':
    print '-p is only meaningful for minkowski distance, p is ignored'

# read in word embedings from file
word_embs = {}
with open('res/word_embs.tsv') as f:
    for line in f.readlines():
        splt = line.split()
        word_embs[splt[0]] = np.array([float(i) for i in splt[1:]])

# vector distance measures
def euclidean(x, y):
    return np.linalg.norm(x-y)

def manhattan(x, y):
    return sum(abs(x-y) for x,y in zip(x,y))

def minkowski(x, y):
    p = 3
    if args.p:
        p = args.p
    expo = Fraction.from_float(float(1)/float(p))
    return sum(pow(abs(xi-yi),p) for xi,yi in zip(x,y))**expo


# get the next k neighboring words for a given vector
def next_words_vector(vector, k=5, dist_func=euclidean, exclude=[]):
    # go through all vectors and calculate their distance to the given vector (except the given words own vector)
    # we get a list of tuples (word, distance to given word)
    result = [(w, dist_func(vector, v)) for w, v in word_embs.iteritems() if w not in exclude]
    # sort the resulting list a by distance and return the first k items of that list
    return sorted(result, key=operator.itemgetter(1))[:k]

# get the neighboring words given a word, this is just forwarding to next_words_vector()
def next_words(word, k=5, dist_func=euclidean):
    return next_words_vector(word_embs[word], k=k, dist_func=dist_func, exclude=[word])

# get the chosen distance function from the command line string
df = globals()[args.distance]

# either we get a word with -w
if len(args.word) == 1:
    word = args.word[0]
    print 'Next {} words to {} with associated distance measure:'.format(args.k, word)
    for next_word, dist in next_words(word, k=args.k, dist_func=df):
        print next_word, '\t\t', dist
# or a 50d vector with -v
elif len(args.word) > 1:
    vec = sum([word_embs[word] for word in args.word])
    print 'Next {} words to {} with associated distance measure:'.format(args.k, args.word)
    for next_word, dist in next_words_vector(vec, k=args.k, dist_func=df, exclude=args.word):
        print next_word, '\t\t', dist
else:
    print 'Next {} words to given vector with associated distance measure:'.format(args.k)
    for next_word, dist in next_words_vector(args.vector, k=args.k, dist_func=df):
        print next_word, '\t\t', dist
