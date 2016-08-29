#! /usr/bin/env python
# -*- coding: utf-8 -*-
from collections import Counter
from sklearn.grid_search import GridSearchCV, RandomizedSearchCV

from sklearn.cross_validation import train_test_split
from sklearn.feature_selection.univariate_selection import SelectKBest, SelectPercentile
from sklearn.metrics.classification import classification_report
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.dict_vectorizer import DictVectorizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics import precision_score

from sklearn.feature_selection import chi2

from sklearn.base import TransformerMixin

from sklearn.pipeline import Pipeline, FeatureUnion, make_pipeline

from sklearn.feature_extraction.text import CountVectorizer

import nltk
import re

class SentimentFeatureExtractor(TransformerMixin):

    def ngrams(self, tokens):
        for i in range(len(tokens)):
            yield tokens[i]
            if i+1 < len(tokens):
                yield ' '.join(tokens[i:i+2])
            if i+2 < len(tokens):
                yield ' '.join(tokens[i:i+3])

    def regex_or(self, *items):
        return '(?:' + '|'.join(items) + ')'

    def getEmoticonRegex(self):
        #  Emoticons
        # myleott: in Python the (?iu) flags affect the whole expression
        #normalEyes = "(?iu)[:=]" # 8 and x are eyes but cause problems
        normalEyes = "[:=]" # 8 and x are eyes but cause problems
        wink = "[;]"
        noseArea = "(?:|-|[^a-zA-Z0-9 ])" # doesn't get :'-(
        happyMouths = r"[D\)\]\}]+"
        sadMouths = r"[\(\[\{]+"
        tongue = "[pPd3]+"
        otherMouths = r"(?:[oO]+|[/\\]+|[vV]+|[Ss]+|[|]+)" # remove forward slash if http://'s aren't cleaned

        # mouth repetition examples:
        # @aliciakeys Put it in a love song :-))
        # @hellocalyclops =))=))=)) Oh well

        # myleott: try to be as case insensitive as possible, but still not perfect, e.g., o.O fails
        #bfLeft = u"(♥|0|o|°|v|\\$|t|x|;|\u0ca0|@|ʘ|•|・|◕|\\^|¬|\\*)".encode('utf-8')
        bfLeft = u"(♥|0|[oO]|°|[vV]|\\$|[tT]|[xX]|;|\u0ca0|@|ʘ|•|・|◕|\\^|¬|\\*)".encode('utf-8')
        bfCenter = r"(?:[\.]|[_-]+)"
        bfRight = r"\2"
        s3 = r"(?:--['\"])"
        s4 = r"(?:<|&lt;|>|&gt;)[\._-]+(?:<|&lt;|>|&gt;)"
        s5 = "(?:[.][_]+[.])"
        # myleott: in Python the (?i) flag affects the whole expression
        #basicface = "(?:(?i)" +bfLeft+bfCenter+bfRight+ ")|" +s3+ "|" +s4+ "|" + s5
        basicface = "(?:" +bfLeft+bfCenter+bfRight+ ")|" +s3+ "|" +s4+ "|" + s5

        eeLeft = r"[＼\\ƪԄ\(（<>;ヽ\-=~\*]+"
        eeRight= u"[\\-=\\);'\u0022<>ʃ）/／ノﾉ丿╯σっµ~\\*]+".encode('utf-8')
        eeSymbol = r"[^A-Za-z0-9\s\(\)\*:=-]"
        eastEmote = eeLeft + "(?:"+basicface+"|" +eeSymbol+")+" + eeRight

        oOEmote = r"(?:[oO]" + bfCenter + r"[oO])"


        emoticon = self.regex_or(
                # Standard version  :) :( :] :D :P
                "(?:>|&gt;)?" + self.regex_or(normalEyes, wink) + self.regex_or(noseArea,"[Oo]") + self.regex_or(tongue+r"(?=\W|$|RT|rt|Rt)", otherMouths+r"(?=\W|$|RT|rt|Rt)", sadMouths, happyMouths),

                # reversed version (: D:  use positive lookbehind to remove "(word):"
                # because eyes on the right side is more ambiguous with the standard usage of : ;
                self.regex_or("(?<=(?: ))", "(?<=(?:^))") + self.regex_or(sadMouths,happyMouths,otherMouths) + noseArea + self.regex_or(normalEyes, wink) + "(?:<|&lt;)?",

                #inspired by http://en.wikipedia.org/wiki/User:Scapler/emoticons#East_Asian_style
                eastEmote.replace("2", "1", 1), basicface,
                # iOS 'emoji' characters (some smileys, some symbols) [\ue001-\uebbb]
                # TODO should try a big precompiled lexicon from Wikipedia, Dan Ramage told me (BTO) he does this

                # myleott: o.O and O.o are two of the biggest sources of differences
                #          between this and the Java version. One little hack won't hurt...
                oOEmote
        )

        return emoticon

    def transform(self, samples, **kwargs):
        #cv = CountVectorizer(analyzer='word', ngram_range=(1,8), max_features=100)
        #cv.fit(X)
        samples_transformed = []
        emoticons = re.compile(self.getEmoticonRegex())

        #hier wird für jedes Sample ein dictionary erzeug
        for sample in samples:  # jedes sample ist ein Text

            words = sample.split()

            feats = Counter()

            feats = feats + Counter(nltk.pos_tag(sample))

            for word in words:
                if feats.get(word):
                    feats[word] += 1
                else:
                    feats[word] = 1

                s = re.search(emoticons, word)
                if s:
                    e = s.group()
                    if feats.get(e):
                        feats[e] += 1
                    else:
                        feats[e] = 1

            # ngrams = self.ngrams(words)
            # for n in ngrams:
            #     if feats.get(n):
            #         feats[n] += 1
            #     else:
            #         feats[n] = 1

           #  bigrams = {}
           #  bigrams_c = 0
           #  trigrams = {}
           #  trigrams_c = 0
           #
           #  feats = {}
           #
           #  # TODO: hier fügen wir features als Einträge des dicts ein
           #  # AUFGABE: 3 interessante Features implementieren!!
           #
           #  # vorerst nehmen die counts der Wörter als features
           #  x
           #
           #  # filtern: nur Adjektive
           #  filtered_words = []
           #  for tag in nltk.pos_tag(words):
           #      if tag[1].startswith('J'):
           #          filtered_words.append(tag[0])
           #  #words = filtered_words
           #
           #
           #  for adjective in filtered_words:
           #      if feats.get(adjective):
           #          feats[adjective] += 1
           #      else:
           #          feats[adjective] = 1
           #
           #  # ideen für weitere Features:
           #  #
           #  # NEGATION HANDLING!!!
           #  # eine einfache implementierung kann hier gefunden werden:
           #  # https://github.com/vivekn/sentiment-web/blob/master/info.py
           #  # ngrams
           #  for item in nltk.bigrams(words):
           #      bigrams_id = 0
           #      if not bigrams.get(item):
           #          bigrams_c += 1
           #          bigrams[item] = bigrams_c
           #          bigrams_id = bigrams_c
           #      else:
           #          bigrams_id = bigrams.get(item)
           #      feats["bigram_id"] = bigrams_id
           #
           #  for item in nltk.trigrams(words):
           #      trigrams_id = 0
           #      if not trigrams.get(item):
           #          trigrams_c = trigrams_c+1
           #          trigrams[item] = trigrams_c
           #          trigrams_id = trigrams_c
           #      else:
           #          trigrams_id = trigrams.get(item)
           #      feats["trigram_id"] = trigrams_id
           #  # c = 0
           #  # for e in cv.transform(sample).toarray():
           #  #     for e2 in e:
           #  #         feats[c] = e2
           #  #         c = c+1
           #  #feats["ngram"] = cv.transform(sample).toarray().tolist()
           # #POS tags
           #  #pos anzahl der vorkommen
           #  tags = [t for w, t in nltk.pos_tag(words)]
           #  for tag in tags:
           #      if feats.get(tag):
           #          feats[tag] += 1
           #      else:
           #          feats[tag] = 1
           #  # lemmatized words
           #  # besserer tokenizer als split() (aber die Texte sind schon sehr sauber, sollte nicht nötig sein)
           #  # ...

            samples_transformed.append(feats)
        return samples_transformed

    def fit(self, X, y):
        return self

    # get_params and set_params so we can use grid search for parameters we might set
    def get_params(self, deep=True):
        # return a dict of this transformers attributes like so:
        # return {"attr1": self.attr1, "attr2": self.attr2}
        return {}

    def set_params(self, **parameters):
        for parameter, value in parameters.items():
            self.setattr(parameter, value)
        return self

# class Stack(TransformerMixin):
#
#     def transform(self, X, **kwargs):

X = []  # samples
y = []  # labels

with open('res/sentiment_corpus.tsv') as f:  # einlesen des Corpus
    for line in f.readlines():
        splt = line.split('\t')
        y.append(splt[0].strip())
        X.append(splt[1].strip())

X_train, X_test, y_train, y_test = train_test_split(X, y)  # train test Split
# TODO: train set in train und dev unterteilen, oder ... s. unten

feat_extr = FeatureUnion([
    ('our_fextractor', Pipeline([('extract', SentimentFeatureExtractor()),
                                 ('transform', DictVectorizer())])),
    ('sklearn_fextractor', CountVectorizer(ngram_range=(1, 4)))
])

pipe = Pipeline([
    ('feature_extractor', feat_extr),  # unser feature extractor von oben
    #('dict_vectorizer', DictVectorizer()),               # macht aus unseren dicts Vectoren
    ('tfidf', TfidfTransformer()),
    ('feature_selection', SelectPercentile(score_func=chi2, percentile=50)),
    ('classifier', MultinomialNB())
])                    # der eigentliche Classifier

param_grid= [{'classifier__alpha': [0.1,0.2,0.01], 'feature_extractor__sklearn_fextractor__ngram_range': [(1,2), (2,3), (4,6)],
              'feature_selection__percentile': [50,60,90]}]

searcher = GridSearchCV(pipe,param_grid,score_func='precision', n_jobs=-1)

#searcher = GridSearchCV(pipe,param_grid,score_func='precision', n_jobs=-1)
#searcher = GridSearchCV(pipe,param_grid,score_func=precision_score)

#RandomizedSearchCV()

# TODO: anstatt eines manuellen train/dev Splits können wir auch Crossfolding nutzen:
# sklearn.cross_validation

# TODO: um die richtigen Parameter zu finden:
# sklearn.grid_search.GridSearchCV
# Obacht! hierfür müssen wir wahrscheinlich für unseren FeatureExtractor die methode set_params implementieren!!

searcher.fit(X_train, y_train)

#print searcher.best_params_
print "ab"
print classification_report(y_test, searcher.predict(X_test))
