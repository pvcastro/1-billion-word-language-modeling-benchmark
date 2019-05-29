#!/usr/bin/env python
# coding: utf-8

from gensim.models import Word2Vec, FastText
from os import cpu_count
import logging


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


juridico_corpus_path = '/home/corpora/full_5B/full_nilc.txt'


model_w2v_cbow = Word2Vec(corpus_file=juridico_corpus_path, sg=0, workers=cpu_count())
model_w2v_cbow.wv.save_word2vec_format('/home/models/embeddings/word2vec_jur/c100_5B-nilc')

model_w2v_skip = Word2Vec(corpus_file=juridico_corpus_path, sg=1, workers=cpu_count())
model_w2v_skip.wv.save_word2vec_format('/home/models/embeddings/word2vec_jur/s100_5B-nilc')

model_ft_cbow = FastText(corpus_file=juridico_corpus_path, sg=0, workers=cpu_count())
model_ft_cbow.wv.save_word2vec_format('/home/models/embeddings/fasttext_jur/c100_5B-nilc')

model_ft_skip = FastText(corpus_file=juridico_corpus_path, sg=1, workers=cpu_count())
model_ft_skip.wv.save_word2vec_format('/home/models/embeddings/fasttext_jur/s100_5B-nilc')
