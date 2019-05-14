import sentencepiece as spm

spm.SentencePieceTrainer.Train('--input=/media/discoD/repositorios/1-billion-word-language-modeling-benchmark/wiki-bert/wiki.bert.txt --model_prefix=bert_pt --character_coverage=1.0 --vocab_size=30000 --model_type=word')
