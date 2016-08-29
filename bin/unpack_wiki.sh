#!/bin/sh

# cd into res/wiki_downloads and unpack every .bz2 file found (do not keep original file)
# TODO check if files in directory are the correct ones
cd ../res/wiki_downloads

find . -name '*.bz2' -exec bzip2 -d {} +
