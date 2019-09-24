#!/bin/bash

# Copyright 2013 Google Inc. All rights reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Does all the corpus preparation work.
#
# Assumes ptwiki-latest-pages-articles.xml.bz2 (downloaded from https://dumps.wikimedia.org/ptwiki/latest/)
# have already been extracted by https://github.com/attardi/wikiextractor using:
# WikiExtractor.py -b 2G ptwiki-latest-pages-articles.xml.bz2 (the parameter -b 2G produces a single file for the whole dump)
#
# The extracted text file are extracted into a folder which must be set as $WIKI_FILE
#
# Takes the data in:
# $WIKI_FILE, strips xml tags which separates each document in wiki, removes duplication with sort -u.
# Removes lines that contains only numbers and puncuation, shuffles every sentence, and runs punctuation
# normalization and tokenization, producing the data in ./wiki-processed/wiki.tokenized.txt
#
# It then splits the data in 100 shards, randomly shuffled, sets aside
# held-out data, and splits it into 50 test partitions.

echo $WIKI_FILE

if [ -d wiki-processed ]
then
  rm -rf wiki-processed/*
else
  mkdir wiki-processed
fi

FOLDER=$WIKI_FILE

printf "\n***** file $WIKI_FILE *****\n"

#python ./scripts/strip_xml.py "$WIKI_FILE"

echo "Sorting $WIKI_FILE"
cat "$WIKI_FILE" | sort -u --output=wiki-processed/wiki.sort.txt
echo "Done sorting $WIKI_FILE"

python ./scripts/strip_special_lines.py wiki-processed/wiki.sort.txt wiki-processed/wiki.sort.clean.txt wiki-processed/wiki.sort.filtered.txt

echo "Shuffling lines from clean file"
shuf wiki-processed/wiki.sort.clean.txt > wiki-processed/wiki.shuffled.txt
echo "Done shuffling lines"

# Set environemnt vars LANG and LANGUAGE to make sure all users have the same locale settings.
export LANG=pt_BR.UTF-8
export LANGUAGE=pt_BR:
export LC_ALL=pt_BR.UTF-8

echo "Tokenizing shuffled file"
time cat wiki-processed/wiki.shuffled.txt | \
  ./scripts/normalize-punctuation.perl -l pt | \
  ./scripts/tokenizer.perl -l pt > \
  wiki-processed/wiki.tokenized.txt
echo "Done tokenizing"

# Split the data in 100 shards
if [ -d training-wiki ]
then
  rm -rf training-wiki/*
else
  mkdir training-wiki
fi
./scripts/split-input-data.perl \
  --output_file_base="$PWD/training-wiki/wiki" \
  --num_shards=100 \
  --input_file=wiki-processed/wiki.tokenized.txt
echo "Done splitting corpus into 100 shards wiki-000??-of-00100."

# Hold 00000 shard out, and split it 50 way.
if [ -d heldout-wiki ]
then
  rm -rf heldout-wiki/*
else
  mkdir heldout-wiki
fi

mv ./training-wiki/wiki-00000-of-00100 \
  heldout-wiki/
echo "Set aside shard 00000 of wiki-000??-of-00100 as held-out data."

./scripts/split-input-data.perl \
  --output_file_base="$PWD/heldout-wiki/wiki.heldout" \
  --num_shards=50 \
  --input_file=heldout-wiki/wiki-00000-of-00100
echo "Done splitting held-out data into 50 shards."

rm -rf heldout-wiki/wiki-00000-of-00100

if [ -d training-wiki.tar.gz ]
then
    rm -rf training-wiki.tar.gz
    rm -rf heldout-wiki.tar.gz
else
    tar -czvf training-wiki.tar.gz training-wiki
    tar -czvf heldout-wiki.tar.gz heldout-wiki
fi

echo "python ./scripts/generate_vocabulary.py --corpus-prefix wiki --path-in "$(pwd)""
