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
# Assumes ptharem-latest-pages-articles.xml.bz2 (downloaded from https://dumps.haremmedia.org/ptharem/latest/)
# have already been extracted by https://github.com/attardi/haremextractor using:
# WikiExtractor.py -b 2G ptharem-latest-pages-articles.xml.bz2 (the parameter -b 2G produces a single file for the whole dump)
#
# The extracted text file are extracted into a folder which must be set as $HAREM_FILE
#
# Takes the data in:
# $HAREM_FILE, strips xml tags which separates each document in harem, removes duplication with sort -u.
# Removes lines that contains only numbers and puncuation, shuffles every sentence, and runs punctuation
# normalization and tokenization, producing the data in ./harem-processed/harem.tokenized.txt
#
# It then splits the data in 100 shards, randomly shuffled, sets aside
# held-out data, and splits it into 50 test partitions.

echo $HAREM_FILE

if [ -d harem-processed ]
then
  rm -rf harem-processed/*
else
  mkdir harem-processed
fi

FOLDER=$HAREM_FILE

printf "\n***** file $HAREM_FILE *****\n"

python ./scripts/strip_xml.py "$HAREM_FILE"

echo "Sorting $HAREM_FILE"
cat "$HAREM_FILE" | sort -u --output=harem-processed/harem.sort.txt
echo "Done sorting $HAREM_FILE"

python ./scripts/strip_special_lines.py harem-processed/harem.sort.txt harem-processed/harem.sort.clean.txt harem-processed/harem.sort.filtered.txt

echo "Shuffling lines from clean file"
shuf harem-processed/harem.sort.clean.txt > harem-processed/harem.shuffled.txt
echo "Done shuffling lines"

# Set environemnt vars LANG and LANGUAGE to make sure all users have the same locale settings.
export LANG=pt_BR.UTF-8
export LANGUAGE=pt_BR:
export LC_ALL=pt_BR.UTF-8

echo "Tokenizing shuffled file"
time cat harem-processed/harem.shuffled.txt | \
  ./scripts/normalize-punctuation.perl -l pt | \
  ./scripts/tokenizer.perl -l pt > \
  harem-processed/harem.tokenized.txt
echo "Done tokenizing"

# Split the data in 100 shards
if [ -d training-harem ]
then
  rm -rf training-harem/*
else
  mkdir training-harem
fi
./scripts/split-input-data.perl \
  --output_file_base="$PWD/training-harem/harem" \
  --num_shards=10 \
  --input_file=harem-processed/harem.tokenized.txt
echo "Done splitting corpus into 10 shards harem-000??-of-00010."

# Hold 00000 shard out, and split it 50 way.
if [ -d heldout-harem ]
then
  rm -rf heldout-harem/*
else
  mkdir heldout-harem
fi

mv ./training-harem/harem-00000-of-00010 \
  heldout-harem/
echo "Set aside shard 00000 of harem-000??-of-00010 as held-out data."

./scripts/split-input-data.perl \
  --output_file_base="$PWD/heldout-harem/harem.heldout" \
  --num_shards=1 \
  --input_file=heldout-harem/harem-00000-of-00010
echo "Done splitting held-out data into 1 shard."

rm -rf heldout-harem/harem-00000-of-00010

if [ -d training-harem.tar.gz ]
then
    rm -rf training-harem.tar.gz
    rm -rf heldout-harem.tar.gz
else
    tar -czvf training-harem.tar.gz training-harem
    tar -czvf heldout-harem.tar.gz heldout-harem
fi

echo "python ./scripts/generate_vocabulary.py --corpus-prefix harem --path-in "$(pwd)""
