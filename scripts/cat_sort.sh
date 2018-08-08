#!/bin/bash

rm -rf wiki_sub_1.txt
rm -rf wiki_sub_2.txt
rm -rf wiki_sub_3.txt
rm -rf wiki_sub_4.txt
rm -rf wiki_sub_5.txt

cat "/media/discoD/Corpora/Portuguese Wikipedia Dump/wiki.sorted.clean.txt" | tail -n +200000 | head -n 10 > wiki_sub_1.txt
cat "/media/discoD/Corpora/Portuguese Wikipedia Dump/wiki.sorted.clean.txt" | tail -n +300000 | head -n 10 > wiki_sub_2.txt
cat "/media/discoD/Corpora/Portuguese Wikipedia Dump/wiki.sorted.clean.txt" | tail -n +400000 | head -n 10 > wiki_sub_3.txt
cat "/media/discoD/Corpora/Portuguese Wikipedia Dump/wiki.sorted.clean.txt" | tail -n +500000 | head -n 10 > wiki_sub_4.txt
cat "/media/discoD/Corpora/Portuguese Wikipedia Dump/wiki.sorted.clean.txt" | tail -n +600000 | head -n 10 > wiki_sub_5.txt

for i in {1..5}
do
    echo "wiki_sub_"$i".txt"
    cat "wiki_sub_"$i".txt"
done | sort -u --output=wiki_sub.txt

#
#
## Unique sort of the sentences in the corpus. Quite a few sentences are replicated,
## dropping the number of words from about 2.9B to about 0.8B.  Use binary/C ordering.
#export LC_ALL=C
#for year in 2007 2008 2009 2010 2011; do
#  cat $TM_FOLDER/training-monolingual/news.${year}.en.shuffled
#done | sort -u --output=training-monolingual.tokenized/news.20XX.en.shuffled.sorted
#echo "Done sorting corpus."
#
## Set environemnt vars LANG and LANGUAGE to make sure all users have the same
## locale settings.
#export LANG=en_US.UTF-8
#export LANGUAGE=en_US:
#export LC_ALL=en_US.UTF-8
#
#echo "Working on training-monolingual/news.20XX.en.shuffled.sorted"
#time cat training-monolingual.tokenized/news.20XX.en.shuffled.sorted | \
#  ./scripts/normalize-punctuation.perl -l en | \
#  ./scripts/tokenizer.perl -l en > \
#  training-monolingual.tokenized/news.20XX.en.shuffled.sorted.tokenized
#echo "Done working on training-monolingual/news.20XX.en.shuffled."
#
## Split the data in 100 shards
#if [ -d training-monolingual.tokenized.shuffled ]
#then
#  rm -rf training-monolingual.tokenized.shuffled/*
#else
#  mkdir training-monolingual.tokenized.shuffled
#fi
#./scripts/split-input-data.perl \
#  --output_file_base="$PWD/training-monolingual.tokenized.shuffled/news.en" \
#  --num_shards=100 \
#  --input_file=training-monolingual.tokenized/news.20XX.en.shuffled.sorted.tokenized
#echo "Done splitting/shuffling corpus into 100 shards news.en-000??-of-00100."
#
## Hold 00000 shard out, and split it 50 way.
#if [ -d heldout-monolingual.tokenized.shuffled ]
#then
#  rm -rf heldout-monolingual.tokenized.shuffled/*
#else
#  mkdir heldout-monolingual.tokenized.shuffled
#fi
#
#mv ./training-monolingual.tokenized.shuffled/news.en-00000-of-00100 \
#  heldout-monolingual.tokenized.shuffled/
#echo "Set aside shard 00000 of news.en-000??-of-00100 as held-out data."
#
#./scripts/split-input-data.perl \
#  --output_file_base="$PWD/heldout-monolingual.tokenized.shuffled/news.en.heldout" \
#  --num_shards=50 \
#  --input_file=heldout-monolingual.tokenized.shuffled/news.en-00000-of-00100
#echo "Done splitting/shuffling held-out data into 50 shards."
