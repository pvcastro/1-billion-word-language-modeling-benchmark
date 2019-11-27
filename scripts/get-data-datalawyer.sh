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
# Assumes ptdatalawyer-latest-pages-articles.xml.bz2 (downloaded from https://dumps.datalawyermedia.org/ptdatalawyer/latest/)
# have already been extracted by https://github.com/attardi/datalawyerextractor using:
# WikiExtractor.py -b 2G ptdatalawyer-latest-pages-articles.xml.bz2 (the parameter -b 2G produces a single file for the whole dump)
#
# The extracted text file are extracted into a folder which must be set as ${DATALAWYER_FILE}
#
# Takes the data in:
# ${DATALAWYER_FILE}, strips xml tags which separates each document in datalawyer, removes duplication with sort -u.
# Removes lines that contains only numbers and puncuation, shuffles every sentence, and runs punctuation
# normalization and tokenization, producing the data in ./datalawyer-processed/datalawyer.tokenized.txt
#
# It then splits the data in 100 shards, randomly shuffled, sets aside
# held-out data, and splits it into 50 test partitions.

echo ${DATALAWYER_FILE}

if [[ -d datalawyer-processed ]]
then
  rm -rf datalawyer-processed/*
else
  mkdir datalawyer-processed
fi

FOLDER=${DATALAWYER_FILE}

printf "\n***** file ${DATALAWYER_FILE} *****\n"

#python ./scripts/strip_xml.py "${DATALAWYER_FILE}"

echo "Sorting ${DATALAWYER_FILE}"
cat "${DATALAWYER_FILE}" | sort -u --output=datalawyer-processed/datalawyer.sort.txt
echo "Done sorting ${DATALAWYER_FILE}"

python ./scripts/strip_special_lines.py datalawyer-processed/datalawyer.sort.txt datalawyer-processed/datalawyer.sort.clean.txt datalawyer-processed/datalawyer.sort.filtered.txt

echo "Shuffling lines from clean file"
shuf datalawyer-processed/datalawyer.sort.clean.txt > datalawyer-processed/datalawyer.shuffled.txt
echo "Done shuffling lines"

# Set environemnt vars LANG and LANGUAGE to make sure all users have the same locale settings.
export LANG=pt_BR.UTF-8
export LANGUAGE=pt_BR:
export LC_ALL=pt_BR.UTF-8

echo "Tokenizing shuffled file"
time cat datalawyer-processed/datalawyer.shuffled.txt | \
  ./scripts/normalize-punctuation.perl -l pt | \
  ./scripts/tokenizer.perl -l pt > \
  datalawyer-processed/datalawyer.tokenized.txt
echo "Done tokenizing"

# Split the data in 100 shards
if [[ -d training-datalawyer ]]
then
  rm -rf training-datalawyer/*
else
  mkdir training-datalawyer
fi
./scripts/split-input-data.perl \
  --output_file_base="$PWD/training-datalawyer/datalawyer" \
  --num_shards=10 \
  --input_file=datalawyer-processed/datalawyer.tokenized.txt
echo "Done splitting corpus into 10 shards datalawyer-000??-of-00010."

# Hold 00000 shard out, and split it 50 way.
if [[ -d heldout-datalawyer ]]
then
  rm -rf heldout-datalawyer/*
else
  mkdir heldout-datalawyer
fi

mv ./training-datalawyer/datalawyer-00000-of-00010 \
  heldout-datalawyer/
echo "Set aside shard 00000 of datalawyer-000??-of-00010 as held-out data."

./scripts/split-input-data.perl \
  --output_file_base="$PWD/heldout-datalawyer/datalawyer.heldout" \
  --num_shards=1 \
  --input_file=heldout-datalawyer/datalawyer-00000-of-00010
echo "Done splitting held-out data into 1 shard."

rm -rf heldout-datalawyer/datalawyer-00000-of-00010

if [[ -d training-datalawyer.tar.gz ]]
then
    rm -rf training-datalawyer.tar.gz
    rm -rf heldout-datalawyer.tar.gz
else
    tar -czvf training-datalawyer.tar.gz training-datalawyer
    tar -czvf heldout-datalawyer.tar.gz heldout-datalawyer
fi

echo "python ./scripts/generate_vocabulary.py --corpus-prefix datalawyer --path-in "$(pwd)""
