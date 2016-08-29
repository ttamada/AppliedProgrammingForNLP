#! /usr/bin/env python
# -*- coding: utf-8 -*-

import fileinput

compounds = set()
noncompounds = set()

#TODO: improve these lists!!!
# some entries might remove candidates one could argue about
# some entries also might remove clear non-compounds...
# some compounds still recognized:
#Bildschirm
#Großmutter
#Jahrestag
compound_substrs = ['df',
                    'ds'
                    'dt',  # arguable
                    'gf',
                    'gs',
                    'gt',
                    'nb',
                    'sd',
                    'sf',
                    'ßf',
                    'sg'
                    'tf',
                    'tk',
                    'tst']

common_compwrds = ['anlage',
                   'ball',
                   'geld',
                   'haus',
                   'kerl',
                   'kind',
                   'mutter',
                   'nummer',
                   'spiel',
                   'spieler',
                   'stoff',
                   'teil',
                   'vater',
                   'wagen']

printed = set()

def print_if_no_compound(a_string):
    # only print once
    if a_string in printed:
        return
    # ignore words longer than 13 chars
    # also ignore short artifacts
    if len(a_string) > 13 or len(a_string) < 4:
        return
    # ignore words containing words (but not being equal!!) often appearing in compounds
    for wrd in common_compwrds:
        if wrd in a_string.lower() and not wrd == a_string.lower():
            return
    # ignore words containing character sequences typically appearing in compounds
    for substr in compound_substrs:
        if substr in a_string:
            # word does contain weird char sequences which might be compoundish
            return
    #print everything else
    #TODO: this does still contain proper nouns... Do we want these?
    if a_string not in printed:
        print a_string
        printed.add(a_string)


for line in fileinput.input():
    splt = line.split()
    #only nouns that were recognized are taken into account
    if splt[1].startswith('N') and splt[2] != '<unknown>':
        print_if_no_compound(splt[2]) #TODO: should we use full form (splt[0]) here?

# and just for fun add these:
print 'Ei'
print 'Eis'
