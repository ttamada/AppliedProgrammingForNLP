#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import argparse
from numpy.random import choice

from dream_machine_utils import replace_tags, count_ngrams

parser = argparse.ArgumentParser(description='generate random text')
parser.add_argument('trainfile', type=str, help='file to generate ngram model from')
#parser.add_argument('-v', '--validate', metavar='VALIDATION FILE', type=str, help='')
parser.add_argument('-n', type=int, default=3, help='order of ngram model to use')
parser.add_argument('-l', '--lower', action='store_true', help='normalizes text always to lower case')
parser.add_argument('-s', '--sentences', metavar='NUM SENTENCES', type=int, default=10, help='number of sentences generated')
parser.add_argument('-m', '--smoothing', type=float, default=0.1, help='count to add for each word (seen or unseen)\n'
                                                                   'additive smoothing. (currently only integers are alowed)')
args = parser.parse_args()

if args.sentences < 1:
    raise Exception('Cannot generate less than 1 sentence')

if args.smoothing <= 0:
    raise Exception('smoothing parameter must be positive')

if args.n < 1:
    raise Exception('n must be greater than 0!')

# read in corpus
# each line is a sentence
with open(args.trainfile, 'r') as f:
    sentences_train = f.readlines()
sentences_validate = []

# some preprocessing
# optionally convert to lower case
if args.lower:
    sentences_train = [s.lower() for s in sentences_train]

sentences_train = [replace_tags(s) for s in sentences_train]

# add sentence start and end tags
sentences_train = [['<s>'] + s.split() + ['</s>'] for s in sentences_train]

# instanciate ngram counts
# this is a list of dicts
# first list: unigrams, second list: bigrams, ... you get the idea
#counts = [{}] * args.n <-- watch out! this does NOT work, since the dict is copied, we must instanciate this like so:
counts = []
for i in range(args.n):
    counts.append({})

count_ngrams(sentences_train, args.n, counts)

vocab = [t[0] for t in counts[0].keys()]  # get string from unigrams (which are stored as "uni-tuples")


# TODO: tune hyper parameters (????)
# if there is a validation file given, do the same as with training file
#    with open(args.validate, 'r') as f:
#        sentences_validate = f.readlines()
#    if args.lower:
#        sentences_validate = [s.lower() for s in sentences_validate]
#    sentences_validate = [replace_tags(s) for s in sentences_validate]
#    sentences_validate = [['<s>'] + s.split() + ['</s>'] for s in sentences_validate]
#    validate_counts = []
#    for i in range(args.n):
#        counts.append({})
#    count_ngrams(sentences_validate, args.n, validate_counts)
#    validate_vocab = validate_counts[0].keys()
#    don't forget smoothing!!


for i in range(args.sentences):
    # we will start with a sentence start tag even if cur_n = 1
    generated_words = ['<s>']

    # and add more words as long as we're not encountering a sentence end tag
    while generated_words[-1] != '</s>' and len(generated_words) < 100:  # TODO: remove second condition
                                                                         # this was just added so the problem
                                                                         # stated in line 107 is avoided...
        context = ()
        if args.n > 1:  # slicing list[-0:] gives the full list, so we'd get the whole sentence instead of nothing
            if len(generated_words) < args.n - 1:
                context = tuple(generated_words)
            else:
                context = tuple(generated_words[-(args.n-1):])

        chose_from = counts[len(context)]
        options = [ngram for ngram in chose_from if ngram[:len(context)] == context]

        op_words_with_counts = {}
        for ngram in options:
            if ngram == ('<s>',):  # for unigram models <s> may appear in options, but we don't want that!
                continue
            op_words_with_counts[ngram[-1]] = chose_from[ngram]

        # adding all other possibilities with count 1 (while increasing all existing counts aswell)
        # for word in vocab:
        #     if word != '<s>':  # we really don't want this!!!
        #         if op_words_with_counts.get(word):
        #             op_words_with_counts[word] += args.smoothing
        #         else:
        #             op_words_with_counts[word] = args.smoothing
        count_sum = sum(op_words_with_counts.values())
        op_probs = [c/count_sum for c in op_words_with_counts.values()]

        #FIXME: problem is, that if we run into sequences we have never seen before due to smoothing,
        # all following cunts equal args.smoothing and we have a chance of 1/len(vocab) to select a sentence end tag...
        # so either choose args.smoothing so small this never happens (and smoothing is useless)
        # or have the second ending condition in this while loop (line 78)
        # oooor increase the count for </s> tremendously... (maybe after a few iterations, but this would be the same
        # as the option mentioned before)

        generated_words.append(choice(op_words_with_counts.keys(), p=op_probs))  # add the last word of the chosen ngram

        # (optional) TODO: interpolation (incorporating models of lower order with some lambda)

    # print the sentence and cut off sentence boundary tags
    print ' '.join(generated_words[1:-1])
