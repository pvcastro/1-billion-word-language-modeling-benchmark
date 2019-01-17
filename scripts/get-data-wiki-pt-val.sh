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



# Split the data in 100 shards
if [ -d wiki-shards ]
then
  rm -rf wiki-shards/*
else
  mkdir wiki-shards
fi
./scripts/split-input-data.perl \
  --output_file_base="$PWD/training-wiki/wiki" \
  --num_shards=100 \
  --input_file=wiki-processed/wiki.tokenized.txt
echo "Done splitting corpus into 100 shards wiki-000??-of-00100."

# Hold 00000 shard out for test
mv ./training-wiki/wiki-00000-of-00100 test.txt
echo "Set aside shard 00000 of wiki-00000-of-00100 as test data."

# Hold 00000 shard out for validation
mv ./training-wiki/wiki-00001-of-00100 valid.txt
echo "Set aside shard 00000 of wiki-00001-of-00100 as validation data."