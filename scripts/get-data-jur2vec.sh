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
# Assumes ptjur2vec-latest-pages-articles.xml.bz2 (downloaded from https://dumps.jurmedia.org/ptjur/latest/)
# have already been extracted by https://github.com/attardi/jurextractor using:
# WikiExtractor.py -b 2G ptjur2vec-latest-pages-articles.xml.bz2 (the parameter -b 2G produces a single file for the whole dump)
#
# The extracted text file are extracted into a folder which must be set as ${JUR_FILE}
#
# Takes the data in:
# ${JUR_FILE}, strips xml tags which separates each document in jur, removes duplication with sort -u.
# Removes lines that contains only numbers and puncuation, shuffles every sentence, and runs punctuation
# normalization and tokenization, producing the data in ./jur2vec-processed/jur2vec.txt
#
# It then splits the data in 100 shards, randomly shuffled, sets aside
# held-out data, and splits it into 50 test partitions.

echo ${JUR_FILE}

if [[ -d jur2vec-processed ]]
then
  rm -rf jur2vec-processed/*
else
  mkdir jur2vec-processed
fi

FOLDER=${JUR_FILE}

printf "\n***** file ${JUR_FILE} *****\n"

python ./scripts/strip_xml.py "${JUR_FILE}"

python ./scripts/strip_special_lines.py ${JUR_FILE} jur2vec-processed/jur.clean.txt jur2vec-processed/jur.filtered.txt

# Set environemnt vars LANG and LANGUAGE to make sure all users have the same locale settings.
export LANG=pt_BR.UTF-8
export LANGUAGE=pt_BR:
export LC_ALL=pt_BR.UTF-8

echo "Tokenizing shuffled file"
time cat jur2vec-processed/jur.clean.txt | \
  ./scripts/normalize-punctuation.perl -l pt | \
  ./scripts/tokenizer.perl -l pt | \
  ./scripts/lowercase.pl > \
  jur2vec-processed/jur2vec.txt
echo "Done tokenizing"
