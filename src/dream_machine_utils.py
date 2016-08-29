# -*- coding: utf-8 -*-
def replace_tags(a_string):
    """replace bracket tokens as described here:
    https://www.cis.upenn.edu/~treebank/tokenization.html
    """
    a_string = a_string.replace('-LRB-', '(')
    a_string = a_string.replace('-RRB-', ')')
    a_string = a_string.replace('-LSB-', '[')
    a_string = a_string.replace('-RSB-', ']')
    a_string = a_string.replace('-LCB-', '{')
    return a_string.replace('-RCB-', '}')


def count_ngrams(list_of_split_sentences, n, list_to_fill):
    """fill a list of dicts with ngrams and their counts
    """
    for tokens in list_of_split_sentences:
        for i in range(len(tokens)):
            for j in range(n):  # counts lower than args.n are also taken into account
                if i+n-j <= len(tokens):
                    ngram = tuple(tokens[i:i+n-j])
                    if list_to_fill[n-j-1].get(ngram):
                        list_to_fill[n-j-1][ngram] += 1
                    else:
                        list_to_fill[n-j-1][ngram] = 1