#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import argparse
import math

from dream_machine_utils import replace_tags, count_ngrams

parser = argparse.ArgumentParser(description='test randomly generated text')
parser.add_argument('input', type=str, help='file containing generated text')
parser.add_argument('testfile', type=str, help='file to test generated text on')
parser.add_argument('-n', type=int, default=3, help='order of ngram model to use')
parser.add_argument('-l', '--lower', action='store_true', help='normalizes text always to lower case')
parser.add_argument('-u', '--unknown', type=float, default=.1,
                    help='percentage of vocabulary that is treated as unknown (float between 0 and 1)')
args = parser.parse_args()


if args.n < 1:
    raise Exception('n must be greater than 0!')

if args.unknown <= 0 or args.unknown >= 1:
    raise Exception('u must be between 0 and 1!')

with open(args.input) as f:
    generated_sents = f.readlines()
with open(args.testfile) as f:
    test_sents = f.readlines()

if args.lower:
    generated_sents = [s.lower() for s in generated_sents]
    test_sents = [s.lower() for s in test_sents]

test_sents = [replace_tags(s) for s in test_sents]
generated_sents = [replace_tags(s) for s in generated_sents]

# add sentence start and end tags
split_test_sents = [s.split() for s in test_sents]
generated_sents = [['<s>'] + s.split() + ['</s>'] for s in generated_sents]
test_sents = [['<s>'] + s + ['</s>'] for s in split_test_sents]


# create a frequency dictionary for ngrams in the test file
counts = []
for i in range(args.n):
    counts.append({})
count_ngrams(test_sents, args.n, counts)

# create a vocabulary list (we need to incorporate unknown words to prevent perplexity dropping to 0 when such a word is found)
# counts[0] = list of tuple (word, freq) from test file
vocab = []
for word_freq_tup in counts[0].items():
    if word_freq_tup[1] <= 1 and vocab.count('<unk>') < len(vocab)*args.unknown:
        vocab.append('<unk>')
    else:
        vocab.append(word_freq_tup[0][0])



#iterate through generated sentences
pp = 0

for sentence in generated_sents:

    # replace words that are unknown in test file
    for i in range(len(sentence)):
        if sentence[i] not in vocab:
            sentence[i] = '<unk>'

    log_prob = math.log(1.0) # = 0
    pos = 1

    while pos < len(sentence):
        cur_word = (sentence[pos], )

        context = ()
        if pos < args.n:
            context = tuple(sentence[:pos])
        else:
            context = tuple(sentence[pos-(args.n-1):pos])
        chose_from = counts[len(context)]
        options = [ngram for ngram in chose_from if ngram[:len(context)] == context]


        #probability calculation with laplace smoothing (add-one smoothing)
        if context + cur_word in chose_from:
            actual_ngram_count = chose_from[context + cur_word] + 1
        else:
            actual_ngram_count = 1
        if options != []:
            count_sum = sum([chose_from[ngram] for ngram in options]) + 1*len(counts[0])
        else:
            count_sum = 1*len(counts[0])
        log_prob += math.log(actual_ngram_count/count_sum, 2)


        pos += 1


    sentence_perplexity = math.pow(2.0, (-(1/len(sentence))*log_prob)) # see Week 14:Language modelsIII p.23
                                                             # start and end tag are also taken into account
    pp += sentence_perplexity


ngram = ''
if args.n == 1:
    ngram = "unigram"
elif args.n == 2:
    ngram = "bigram"
elif args.n == 3:
    ngram = "trigram"

print 'Perplexity with ' + ngram + ' model (averaged over sentences):', pp/len(generated_sents)
