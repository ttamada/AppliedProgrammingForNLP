# Makefile template to help you wire together your resource pipeline scripts.
#
# It uses a minimal amount of Make-magic (like automatic variables,
# built-in-functions and custom functions).
# If you think "hey, that looks dumb/redundant", can't we write that more
# elegantly?": yes, we can, but not without more advanced Make features.
#
# See reference at https://www.gnu.org/software/make/manual/make.html
#
# You want to improve this file? Knock yourself out!
#
# Author: David Kaumanns (CIS), April 2015

# This enables Make's interpretation of double $$. Don't worry about it yet.
.SECONDEXPANSION:

# Declarations of source variables.

# Read URLs line-by-line from config file.
urls  = $(shell cat etc/wiki_links.txt)

# Create resource file names from URLs.
files = $(addprefix res/,$(notdir $(urls)))

# set filenames here -- these also act as targets (currently)
corpus_file = res/full_corpus.corpus
vocab_file = res/full_vocab.corpus.vocab
tree_tagged_file = res/full_tagged.corpus.treetagger

token_file = res/full_tokens.corpus.tokens
lemma_file = res/full_lemmas.corpus.lemmas
pos_file = res/full_pos.corpus.pos

# Resource pipeline
#
# Target and prereq files are specified by their extensions. This is
# the "Make" way to setup the dependency chain between files and generally best
# practice for organizing resource files.
# Note the use of automatic variables:
# $< for the (first) prereq and $@ for the target.

# Download the relevant URL for a specific target file.
# (Note: The filtering is just a quick hack to get the relevant URL from the URLs list. Don't worry about it.)
%.bz2:
	wget -O - $(filter %$(notdir $@),$(urls)) > $@

# Unzip the Wiki dump.
%.xml: %.bz2
	bzip2 --keep --decompress --stdout $< > $@

# Tokenize remove remaining XML tags.
# old version
# src/clean_wiki.py $< > $@
# now we're using WikiExtractor
# could use compression mode for WikiExtractor to save space, but would need to call bzip2 again...
# concatenate all output files into one big file and while we're at it remove the lines with <doc> tags
# afterwards remove temporary files
%.corpus: %.xml
	lib/python/WikiExtractor.py -o res/tmp $<
	find res/tmp/ -type f -exec cat {} \; | grep -v -e '^<doc id=' -e '^</doc>' | sed -e 's/<[^>]*>//g' > $@
	rm -rf res/tmp
	

# ---
# You may have your own (intermediate) targets in the pipeline, e.g. two
# different targets for parse and clean. Insert them anywhere.
# ---

# Count words.
# Note: Extensions for derived data like .vocab and .pos (as opposed to transformed data like .corpus)
# is best appended to the original extension.
# replaced by
params ?=
%.corpus.vocab: %.corpus
	src/create_freq_list.py $(params) $< > $@


# Use the CIS TreeTagger to annotate POS.
%.corpus.pos: %.corpus
	cat $< | $(loc-treetagger)/cmd/tree-tagger-english > $@

$(corpus_file): $$(corpus-files)
	cat $^ > $@

$(vocab_file): $(corpus_file)
	src/create_freq_list.py $< > $@

$(tree_tagged_file): $(corpus_file)
	cat $< | $(loc-treetagger)/cmd/tree-tagger-english > $@

$(token_file): $(corpus_file)
	java -cp $(loc-stanford-tagger) edu.stanford.nlp.process.PTBTokenizer $< > $@

$(pos_file): $(token_file)
	java -cp $(loc-stanford-tagger) edu.stanford.nlp.tagger.maxent.MaxentTagger -model $(loc-stanford-tagger-model) -tokenize false -textFile $< | cut -d _ -f2 > $@


# this will cause redundant computations, targets token_file, pos_file and lemma_file could be combined...
# credits to Johannes Baiter for the sed command
$(lemma_file): $(corpus_file)
	java -cp $(loc-stanford-tagger) edu.stanford.nlp.tagger.maxent.MaxentTagger -model $(loc-stanford-tagger-model) -textFile $< -outputFormat xml -outputFormatOptions lemmatize | grep "<word" | sed -e 's/.*lemma="\(.*\)".*/\1/' > $@


# targets for parsing faz.net

res/faz_cats.xml:
	src/parse_faz.py > $@

res/faz_urls.xml: res/faz_cats.xml    
	src/article_urls_from_cats.py $< > $@

# this will create the directory res/faz
# individual files are then written into that directory (this is hard coded in the python script!)
res/faz: res/faz_urls.xml
	src/scrape_faz.py $<

# Hooks into the pipeline (main user interface!)
#
# We declare custom targets with file lists as prereqs. This allows us to make several files with just one make command, e.g. 'make vocab', and hide the
# actual file names from the user.
# (Note: The prereq file variables must be declared with $$ for proper "second expansion". Don't worry about it yet.)


# Some basic targets first - first one will be called by default
# (Do newer make version support the target named 'default' ignoring order?)
default: help

help:
	less README.md

xml:         $$(xml-files)
corpus:      $$(corpus-files)
vocab:       $$(vocab-files)
pos:         $$(pos-files)

# Declarations of target files for all pipeline stages (for the hooks).
# Just replace source file extensions with target file extensions.
# $(call...) just calls a handwritten function. Don't worry about its implementation, just use it.
xml-files        = $(call replace-extension-with,.xml,$(files))
corpus-files     = $(call replace-extension-with,.corpus,$(files))
vocab-files      = $(call replace-extension-with,.corpus.vocab,$(files))
pos-files        = $(call replace-extension-with,.corpus.pos,$(files))

## decomposition stuff

res/frequency_list.txt:
	wget http://thekts.de/temp/de-2012.zip
	unzip de-2012
	mv de.txt $@
	rm de.log de-s.log de-2012.zip

res/compound_list.txt:
	wget -O tmp.txt http://www.sfs.uni-tuebingen.de/lsd/documents/compounds/split_compounds_from_GermaNet10.0.txt
	cat tmp.txt | tail -n+3 > $@
	rm tmp.txt

res/noncompound_list.txt: res/frequency_list.txt
	head -n 150000 $< | cut -d ' ' -f 1 | lib/treetagger/cmd/tree-tagger-german - | src/extract_noncompounds.py > $@

## sentiment stuff

res/sentiment_corpus.tsv:
	wget http://www.cis.uni-muenchen.de/%7Edavidk/ap/res/data/sstb_1000.tsv.bz2
	bzip2 --decompress --stdout sstb_1000.tsv.bz2 | cut -d '	' -f 3,4 > $@
	rm sstb_1000.tsv.bz2
# note that in -d ' ' <-- there is a tab between ' ' as cut does somehow not work with -d$'\t'

## k nearest neighbor stuff

res/word_embs.tsv:
	wget http://www.cis.uni-muenchen.de/~davidk/ap/res/data/word_embs.tsv.bz2
	bzip2 --decompress --stdout word_embs.tsv.bz2 > $@
	rm word_embs.tsv.bz2

res/k_nearest.log:
	./src/k_nearest_neighbor_log.sh > $@


## final project (dream machine)
res/finalProject/generated_sentences_unigram.txt: res/finalProject 
	src/dream_machine.py -n 1 res/wsj/train-wsj-00-20.sent > $@

res/finalProject/generated_sentences_bigram.txt: res/finalProject  
	src/dream_machine.py -n 2 res/wsj/train-wsj-00-20.sent > $@

res/finalProject/generated_sentences_trigram.txt: res/finalProject  
	src/dream_machine.py -n 3 res/wsj/train-wsj-00-20.sent > $@

res/finalProject/dream_machine_model_compare.txt: res/finalProject
	src/dream_machine_test.py res/finalProject/generated_sentences_unigram.txt res/wsj/test-wsj-23-24.sent -n 1 > $@
	src/dream_machine_test.py res/finalProject/generated_sentences_bigram.txt res/wsj/test-wsj-23-24.sent -n 2 >> $@
	src/dream_machine_test.py res/finalProject/generated_sentences_trigram.txt res/wsj/test-wsj-23-24.sent -n 3 >> $@

res/finalProject: 
	mkdir $@


# Don't worry about anything below this line.
# (Doesn't hurt to take a look, though.)
# ------------------------------------------------------------------------------

# Declare some built-in variables.
# It's not always necessary, but good practice in general.
SHELL     = /bin/bash
MAKESHELL = /bin/bash
MAKE      = make

# Functions
replace-extension-with = $(addsuffix $(1),$(basename $(2)))

# Phony targets are targets that we don't want Make to confuse with real files.
# Remember that targets are assumed to be real files by default. E.g., if
# someone created a file "help" in the top directory and we call "make help",
# Make would be satisfied with the file and not print out the help info that we
# actually wanted.
.PHONY: default help install xml corpus vocab pos

# Variables with some third-party library locations.
loc-treetagger      = lib/treetagger
loc-stanford-tagger = lib/java/stanford-tagger.jar
loc-stanford-tagger-model = lib/java/english-left3words-distsim.tagger
loc-wikiextractor   = lib/python/WikiExtractor.py

install:
	mkdir -p res var
	@if [ -e $(loc-stanford-tagger) ]; then echo "Stanford Tagger already installed"; else \
		TAGGER_NAME=stanford-postagger-2014-08-27 \
		&& mkdir -p $(dir $(loc-stanford-tagger)) \
		&& wget http://nlp.stanford.edu/software/$$TAGGER_NAME.zip -O $(loc-stanford-tagger) -O tmp.zip \
		&& unzip tmp.zip -d lib/java \
		&& mv lib/java/$$TAGGER_NAME/stanford-postagger.jar $(loc-stanford-tagger) \
		&& mv lib/java/$$TAGGER_NAME/models/english-left3words-distsim.tagger $(loc-stanford-tagger-model) \
		&& rm -r tmp.zip lib/java/$$TAGGER_NAME; \
	fi
	@if [ -e $(loc-wikiextractor) ]; then echo "WikiExtractor already installed"; else \
		mkdir -p $(dir $(loc-wikiextractor)) \
		&& wget https://raw.githubusercontent.com/bwbaugh/wikipedia-extractor/master/WikiExtractor.py -O $(loc-wikiextractor); \
	fi
	@if [ -e $(loc-treetagger) ]; then echo "TreeTagger already installed"; else \
		mkdir -p $(loc-treetagger) \
		&& cd $(loc-treetagger) \
		&& wget --no-verbose http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/tree-tagger-linux-3.2.tar.gz \
		#&& wget --no-verbose http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/tree-tagger-MacOSX-3.2-intel.tar.gz \
		&& wget --no-verbose http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/tagger-scripts.tar.gz \
		&& wget --no-verbose http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/english-par-linux-3.2-utf8.bin.gz \
		&& wget --no-verbose http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/german-par-linux-3.2-utf8.bin.gz \
		&& wget --no-verbose http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/install-tagger.sh \
		&& chmod a+x install-tagger.sh \
		&& ./install-tagger.sh; \
	fi
