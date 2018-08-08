#!/bin/bash

# Set environemnt vars LANG and LANGUAGE to make sure all users have the same
# locale settings.
export LANG=pt_BR.UTF-8
export LANGUAGE=pt_BR:
export LC_ALL=pt_BR.UTF-8

echo "Tokenizing"
time cat training-wiki/wiki_100.shuffled.txt | \
  ./scripts/normalize-punctuation.perl -l pt | \
  ./scripts/tokenizer.perl -l pt > \
  training-wiki/wiki_100.tokenized.txt
echo "Done tokenizing"
