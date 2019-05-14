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
# normalization and tokenization, producing the data in ./wiki-bert/wiki.tokenized.txt
#
# It then splits the data in 100 shards, randomly shuffled, sets aside
# held-out data, and splits it into 50 test partitions.
source activate fastai

echo $WIKI_FILE
echo $NBP_FILE

if [[ -d wiki-bert ]]
then
  rm -rf wiki-bert/*
else
  mkdir wiki-bert
fi

FOLDER=$WIKI_FILE

printf "\n***** file $WIKI_FILE *****\n"

#python ./scripts/strip_xml.py "$WIKI_FILE"

python ./scripts/split_text.py "$WIKI_FILE" wiki-bert/wiki.bert.txt "$NBP_FILE"

# Set environemnt vars LANG and LANGUAGE to make sure all users have the same locale settings.
export LANG=pt_BR.UTF-8
export LANGUAGE=pt_BR:
export LC_ALL=pt_BR.UTF-8

echo "Tokenizing file"
time cat wiki-bert/wiki.bert.txt | \
  ./scripts/normalize-punctuation.perl -l pt | \
  ./scripts/tokenizer.perl -l pt > \
  wiki-bert/wiki.bert.tokenized.txt
echo "Done tokenizing"

# Split the data in 100 shards
if [[ -d training-bert ]]
then
  rm -rf training-bert/*
else
  mkdir training-bert
fi
./scripts/split-input-data.perl \
  --output_file_base="$PWD/training-bert/bert" \
  --num_shards=100 \
  --input_file=wiki-bert/wiki.bert.tokenized.txt
echo "Done splitting corpus into 100 shards bert-000??-of-00100."

if [[ -d training-bert.tar.gz ]]
then
    rm -rf training-bert.tar.gz
else
    tar -czvf training-bert.tar.gz training-bert
fi

echo "python ./scripts/generate_vocabulary.py --corpus-prefix bert --path-in "$(pwd)""
