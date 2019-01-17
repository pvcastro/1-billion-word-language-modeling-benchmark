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
# Assumes ptjur-latest-pages-articles.xml.bz2 (downloaded from https://dumps.jurmedia.org/ptjur/latest/)
# have already been extracted by https://github.com/attardi/jurextractor using:
# WikiExtractor.py -b 2G ptjur-latest-pages-articles.xml.bz2 (the parameter -b 2G produces a single file for the whole dump)
#
# The extracted text file are extracted into a folder which must be set as $JUR_FILE
#
# Takes the data in:
# $JUR_FILE, strips xml tags which separates each document in jur, removes duplication with sort -u.
# Removes lines that contains only numbers and puncuation, shuffles every sentence, and runs punctuation
# normalization and tokenization, producing the data in ./jur-processed/jur.tokenized.txt
#
# It then splits the data in 100 shards, randomly shuffled, sets aside
# held-out data, and splits it into 50 test partitions.

echo $JUR_FILE

if [ -d jur-processed ]
then
  rm -rf jur-processed/*
else
  mkdir jur-processed
fi

FOLDER=$JUR_FILE

printf "\n***** file $JUR_FILE *****\n"

python ./scripts/strip_xml.py "$JUR_FILE"

echo "Sorting $JUR_FILE"
cat "$JUR_FILE" | sort -u --output=jur-processed/jur.sort.txt
echo "Done sorting $JUR_FILE"

python ./scripts/strip_special_lines.py jur-processed/jur.sort.txt jur-processed/jur.sort.clean.txt jur-processed/jur.sort.filtered.txt

echo "Shuffling lines from clean file"
shuf jur-processed/jur.sort.clean.txt > jur-processed/jur.shuffled.txt
echo "Done shuffling lines"

# Set environemnt vars LANG and LANGUAGE to make sure all users have the same locale settings.
export LANG=pt_BR.UTF-8
export LANGUAGE=pt_BR:
export LC_ALL=pt_BR.UTF-8

echo "Tokenizing shuffled file"
time cat jur-processed/jur.shuffled.txt | \
  ./scripts/normalize-punctuation.perl -l pt | \
  ./scripts/tokenizer.perl -l pt > \
  jur-processed/jur.tokenized.txt
echo "Done tokenizing"

# Split the data in 100 shards
if [ -d training-jur ]
then
  rm -rf training-jur/*
else
  mkdir training-jur
fi
./scripts/split-input-data.perl \
  --output_file_base="$PWD/training-jur/jur" \
  --num_shards=100 \
  --input_file=jur-processed/jur.tokenized.txt
echo "Done splitting corpus into 100 shards jur-000??-of-00100."

# Hold 00000 shard out, and split it 50 way.
if [ -d heldout-jur ]
then
  rm -rf heldout-jur/*
else
  mkdir heldout-jur
fi

mv ./training-jur/jur-00000-of-00100 \
  heldout-jur/
echo "Set aside shard 00000 of jur-000??-of-00100 as held-out data."

./scripts/split-input-data.perl \
  --output_file_base="$PWD/heldout-jur/jur.heldout" \
  --num_shards=50 \
  --input_file=heldout-jur/jur-00000-of-00100
echo "Done splitting held-out data into 50 shards."
