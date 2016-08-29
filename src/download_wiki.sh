#!/bin/sh

# this will download all files specified in etc/wiki_links.txt to res/
wget -i ../etc/wiki_links.txt -P ../res/wiki_downloads/ -nc

#TODO check md5 sums of downloaded files
