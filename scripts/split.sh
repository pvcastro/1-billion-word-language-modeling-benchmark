#!/bin/bash

# Split the data in 100 shards
if [ -d training-wiki ]
then
  rm -rf training-wiki/*
else
  mkdir training-wiki
fi
./scripts/split-input-data.perl \
  --output_file_base="$PWD/training-wiki/wiki" \
  --num_shards=100 \
  --input_file=wiki-processed/wiki.tokenized.txt
echo "Done splitting corpus into 100 shards wiki-000??-of-00100."

# Hold 00000 shard out, and split it 50 way.
if [ -d heldout-wiki ]
then
  rm -rf heldout-wiki/*
else
  mkdir heldout-wiki
fi

mv ./training-wiki/wiki-00000-of-00100 \
  heldout-wiki/
echo "Set aside shard 00000 of wiki-000??-of-00100 as held-out data."

./scripts/split-input-data.perl \
  --output_file_base="$PWD/heldout-wiki/wiki.heldout" \
  --num_shards=50 \
  --input_file=heldout-wiki/wiki-00000-of-00100
echo "Done splitting held-out data into 50 shards."
