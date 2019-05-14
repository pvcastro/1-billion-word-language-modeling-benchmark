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
# Assumes ptiberlef-latest-pages-articles.xml.bz2 (downloaded from https://dumps.iberlefmedia.org/ptiberlef/latest/)
# have already been extracted by https://github.com/attardi/iberlefextractor using:
# WikiExtractor.py -b 2G ptiberlef-latest-pages-articles.xml.bz2 (the parameter -b 2G produces a single file for the whole dump)
#
# The extracted text file are extracted into a folder which must be set as $IBERLEF_FILE
#
# Takes the data in:
# $IBERLEF_FILE, strips xml tags which separates each document in iberlef, removes duplication with sort -u.
# Removes lines that contains only numbers and puncuation, shuffles every sentence, and runs punctuation
# normalization and tokenization, producing the data in ./iberlef-processed/iberlef.tokenized.txt
#
# It then splits the data in 100 shards, randomly shuffled, sets aside
# held-out data, and splits it into 50 test partitions.

echo $IBERLEF_FILE

if [ -d iberlef-processed ]
then
  rm -rf iberlef-processed/*
else
  mkdir iberlef-processed
fi

FOLDER=$IBERLEF_FILE

printf "\n***** file $IBERLEF_FILE *****\n"

python ./scripts/strip_xml.py "$IBERLEF_FILE"

echo "Sorting $IBERLEF_FILE"
cat "$IBERLEF_FILE" | sort -u --output=iberlef-processed/iberlef.sort.txt
echo "Done sorting $IBERLEF_FILE"

python ./scripts/strip_special_lines.py iberlef-processed/iberlef.sort.txt iberlef-processed/iberlef.sort.clean.txt iberlef-processed/iberlef.sort.filtered.txt

echo "Shuffling lines from clean file"
shuf iberlef-processed/iberlef.sort.clean.txt > iberlef-processed/iberlef.shuffled.txt
echo "Done shuffling lines"

# Set environemnt vars LANG and LANGUAGE to make sure all users have the same locale settings.
export LANG=pt_BR.UTF-8
export LANGUAGE=pt_BR:
export LC_ALL=pt_BR.UTF-8

echo "Tokenizing shuffled file"
time cat iberlef-processed/iberlef.shuffled.txt | \
  ./scripts/normalize-punctuation.perl -l pt | \
  ./scripts/tokenizer.perl -l pt > \
  iberlef-processed/iberlef.tokenized.txt
echo "Done tokenizing"

# Split the data in 100 shards
if [ -d training-iberlef ]
then
  rm -rf training-iberlef/*
else
  mkdir training-iberlef
fi
./scripts/split-input-data.perl \
  --output_file_base="$PWD/training-iberlef/iberlef" \
  --num_shards=10 \
  --input_file=iberlef-processed/iberlef.tokenized.txt
echo "Done splitting corpus into 10 shards iberlef-000??-of-00010."

# Hold 00000 shard out, and split it 50 way.
if [ -d heldout-iberlef ]
then
  rm -rf heldout-iberlef/*
else
  mkdir heldout-iberlef
fi

mv ./training-iberlef/iberlef-00000-of-00010 \
  heldout-iberlef/
echo "Set aside shard 00000 of iberlef-000??-of-00010 as held-out data."

./scripts/split-input-data.perl \
  --output_file_base="$PWD/heldout-iberlef/iberlef.heldout" \
  --num_shards=1 \
  --input_file=heldout-iberlef/iberlef-00000-of-00010
echo "Done splitting held-out data into 1 shard."

rm -rf heldout-iberlef/iberlef-00000-of-00010

if [ -d training-iberlef.tar.gz ]
then
    rm -rf training-iberlef.tar.gz
    rm -rf heldout-iberlef.tar.gz
else
    tar -czvf training-iberlef.tar.gz training-iberlef
    tar -czvf heldout-iberlef.tar.gz heldout-iberlef
fi

echo "python ./scripts/generate_vocabulary.py --corpus-prefix iberlef --path-in "$(pwd)""
