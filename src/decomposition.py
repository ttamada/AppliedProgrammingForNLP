#! /usr/bin/env python
# -*- coding: utf-8 -*-

from random import shuffle
import operator


# decorator to use len and getitem for word class
def delegate(method, prop):
    def decorate(cls):
        setattr(cls, method,
            lambda self, *args, **kwargs:
                getattr(getattr(self, prop), method)(*args, **kwargs))
        return cls
    return decorate

@delegate('__len__', 'word')
@delegate('__getitem__', 'word')
class Word(object):

    known_words = set()

    def __init__(self, word, is_compound, head=None, modifiers=None):
        #if not Word.known_words:
        #    raise Exception('please instanciate known words first!')
        self.word = word
        self.is_compound = is_compound
        self.head = head
        self.modifiers = modifiers

    # should return true even if not _all_ modifiers are the same
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        mod_same = False
        if self.modifiers != None and other.modifiers != None:
            for w in self.modifiers:
                if w in other.modifiers:
                    mod_same = True
        if mod_same:
            return self.word == other.word and self.is_compound == other.is_compound and str(self.head).lower() == str(other.head).lower()
        else:
            return False
    
    def __neq__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        if self.is_compound:
            return 'Word: ' + self.word + ' (compound)\n' + \
                   'Head: ' + self.head + '\n' + \
                   'Modifiers: ' + str(self.modifiers)
        else:
            return 'Word: ' + self.word + ' (noncompound)'



# helper method increasing dict counts
def increment_dict_at(a_dict, itm):
    if a_dict.get(itm):
        a_dict[itm] += 1
    else:
        a_dict[itm] = 1


if __name__ == '__main__':

    # read in compounds
    compounds = []
    with open('../res/compound_list.txt') as f:
        for line in f.readlines():
            splt = line.split()
            if len(splt) == 3:  # there is an error in the compound list: for "Kunstflugstaffel" the head is missing!!
                compounds.append(Word(splt[0], True, head=splt[2], modifiers=splt[1].split('|')))

    with open('../res/noncompound_list.txt') as f:
        noncompounds = [Word(line.strip(), False) for line in f.readlines()]

    # TODO: make sure we have more noncompounds than compounds here?
    # problem is we currently do not generate enough NCs from frequency list
    #if len(compounds) > len(noncompounds)/2:
    #    compounds = compounds[:len(noncompounds)/2]

    all_words = compounds + noncompounds
    shuffle(all_words)

    # train/test split
    train = all_words[:int(len(all_words)*.8)]
    test = all_words[int(len(all_words)*.8):]

    # decompounding takes place here
    known_noncompounds = [w.word.lower() for w in train if not w.is_compound]

    fugenelements = ['ens', 'en', 'er', 'es', 'e', 's']
    compound_char_bigrams = set()
    for compound in [w for w in train if w.is_compound]:
        end_of_mods = [m[-1] for m in compound.modifiers]
        start_of_head = compound.head[0]
        for end_char in end_of_mods:
            compound_char_bigrams.add((end_char + start_of_head).lower())

    # will be filled with tuples (actual, result)
    results = []

    for word_to_split in test:
        print 'testing', word_to_split.word
        good_split = {}
        # no need to check for detaching only first or last letter, there are no one character words
        for i in range(1, len(word_to_split)-1):
            first_part = word_to_split[:i].lower()
            second_part = word_to_split[i:].lower()
            # try to find both parts in our
            if first_part in known_noncompounds and second_part in known_noncompounds:
                increment_dict_at(good_split, i)

            # remove fugenelement from first part and try again
            cleaned_first_part = None
            for fugenelement in fugenelements:
                if first_part.endswith(fugenelement):
                    cleaned_first_part = first_part[:len(fugenelement)]
                    break
            if cleaned_first_part:
                if cleaned_first_part in known_noncompounds and second_part in known_noncompounds:
                    increment_dict_at(good_split, i)

            # now lets check if the split lies between two chars that appear often between
            if (first_part[-1] + second_part[0]).lower() in compound_char_bigrams:
                increment_dict_at(good_split, i)

        result = None
        if good_split:
            #print good_split
            split_at = max(good_split.iteritems(), key=operator.itemgetter(1))


            if split_at[1] > 1:
                result = Word(word_to_split.word, True, head=word_to_split[split_at[0]:], modifiers=[word_to_split[:split_at[0]]])
                print "split at", split_at[0]

        if not result:
            result = Word(word_to_split.word, False)

        results.append((word_to_split, result))


    # there is a lot of work to do...
    print 'tested on', len(test), 'words'
    print 'there were', len([w for w in test if w.is_compound]), 'compounds'
    print 'i split', len([tup for tup in results if tup[1].is_compound]), 'of all words'
    print 'i made', len([tup for tup in results if tup[1] == tup[0]]), 'correct decisions'
    #print '(this is just how many words were split or not split, NOT if the split was at the right place)'
    precision = float(len([tup for tup in results if tup[1] == tup[0]]))/float(len([tup for tup in results if tup[1].is_compound]))
    recall = float(len([tup for tup in results if tup[1] == tup[0]]))/float(len([w for w in test if w.is_compound]))
    print 'Precision:', precision
    print 'Recall:', recall
    print 'F1 score:', 2*(precision*recall)/(precision+recall)