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
# Assumes ptlener-latest-pages-articles.xml.bz2 (downloaded from https://dumps.lenermedia.org/ptlener/latest/)
# have already been extracted by https://github.com/attardi/lenerextractor using:
# WikiExtractor.py -b 2G ptlener-latest-pages-articles.xml.bz2 (the parameter -b 2G produces a single file for the whole dump)
#
# The extracted text file are extracted into a folder which must be set as $LENER_FILE
#
# Takes the data in:
# $LENER_FILE, strips xml tags which separates each document in lener, removes duplication with sort -u.
# Removes lines that contains only numbers and puncuation, shuffles every sentence, and runs punctuation
# normalization and tokenization, producing the data in ./lener-processed/lener.tokenized.txt
#
# It then splits the data in 100 shards, randomly shuffled, sets aside
# held-out data, and splits it into 50 test partitions.

echo $LENER_FILE

if [ -d lener-processed ]
then
  rm -rf lener-processed/*
else
  mkdir lener-processed
fi

FOLDER=$LENER_FILE

printf "\n***** file $LENER_FILE *****\n"

python ./scripts/strip_xml.py "$LENER_FILE"

echo "Sorting $LENER_FILE"
cat "$LENER_FILE" | sort -u --output=lener-processed/lener.sort.txt
echo "Done sorting $LENER_FILE"

python ./scripts/strip_special_lines.py lener-processed/lener.sort.txt lener-processed/lener.sort.clean.txt lener-processed/lener.sort.filtered.txt

echo "Shuffling lines from clean file"
shuf lener-processed/lener.sort.clean.txt > lener-processed/lener.shuffled.txt
echo "Done shuffling lines"

# Set environemnt vars LANG and LANGUAGE to make sure all users have the same locale settings.
export LANG=pt_BR.UTF-8
export LANGUAGE=pt_BR:
export LC_ALL=pt_BR.UTF-8

echo "Tokenizing shuffled file"
time cat lener-processed/lener.shuffled.txt | \
  ./scripts/normalize-punctuation.perl -l pt | \
  ./scripts/tokenizer.perl -l pt > \
  lener-processed/lener.tokenized.txt
echo "Done tokenizing"

# Split the data in 100 shards
if [ -d training-lener ]
then
  rm -rf training-lener/*
else
  mkdir training-lener
fi
./scripts/split-input-data.perl \
  --output_file_base="$PWD/training-lener/lener" \
  --num_shards=10 \
  --input_file=lener-processed/lener.tokenized.txt
echo "Done splitting corpus into 10 shards lener-000??-of-00010."

# Hold 00000 shard out, and split it 50 way.
if [ -d heldout-lener ]
then
  rm -rf heldout-lener/*
else
  mkdir heldout-lener
fi

mv ./training-lener/lener-00000-of-00010 \
  heldout-lener/
echo "Set aside shard 00000 of lener-000??-of-00010 as held-out data."

./scripts/split-input-data.perl \
  --output_file_base="$PWD/heldout-lener/lener.heldout" \
  --num_shards=1 \
  --input_file=heldout-lener/lener-00000-of-00010
echo "Done splitting held-out data into 1 shard."

rm -rf heldout-lener/lener-00000-of-00010

if [ -d training-lener.tar.gz ]
then
    rm -rf training-lener.tar.gz
    rm -rf heldout-lener.tar.gz
else
    tar -czvf training-lener.tar.gz training-lener
    tar -czvf heldout-lener.tar.gz heldout-lener
fi

echo "python ./scripts/generate_vocabulary.py --corpus-prefix lener --path-in "$(pwd)""
