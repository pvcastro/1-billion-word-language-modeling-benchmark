# coding: utf-8

from pathlib import Path
from collections import Counter
from itertools import chain

import os, fire, re, csv, pickle

import pandas as pd

from typing import Callable, List, Collection
from concurrent.futures.process import ProcessPoolExecutor

from sacremoses import MosesTokenizer

ORTH = 65


def partition(a: Collection, sz: int) -> List[Collection]:
    "Split iterables `a` in equal parts of size `sz`"
    return [a[i:i + sz] for i in range(0, len(a), sz)]


def partition_by_cores(a: Collection, n_cpus: int) -> List[Collection]:
    "Split data in `a` equally among `n_cpus` cores"
    return partition(a, len(a) // n_cpus + 1)


def num_cpus() -> int:
    "Get number of cpus"
    try:
        return len(os.sched_getaffinity(0))
    except AttributeError:
        return os.cpu_count()


class BaseTokenizer():
    "Basic class for a tokenizer function."

    def __init__(self, lang: str):                      self.lang = lang

    def tokenizer(self, t: str) -> List[str]:           return t.split(' ')


class SpacyTokenizer(BaseTokenizer):
    "Wrapper around a spacy tokenizer to make it a `BaseTokenizer`."

    def __init__(self, lang: str):
        self.tok = MosesTokenizer('pt')

    def tokenizer(self, t: str) -> List[str]:
        return [token for token in self.tok.tokenize(t)]


class VocabularyTokenizer():
    "Put together rules, a tokenizer function and a language to tokenize text with multiprocessing."

    def __init__(self, tok_func: Callable = SpacyTokenizer, lang: str = 'pt', n_cpus: int = None):
        self.tok_func, self.lang = tok_func, lang
        self.n_cpus = n_cpus or num_cpus() // 2

    def process_text(self, t: str, tok: BaseTokenizer) -> List[str]:
        "Processe one text `t` with tokenizer `tok`."
        return tok.tokenizer(t)

    def _process_all_1(self, texts: Collection[str]) -> List[List[str]]:
        "Process a list of `texts` in one process."
        tok = self.tok_func(self.lang)
        return [self.process_text(t, tok) for t in texts]

    def process_all(self, texts: Collection[str]) -> List[List[str]]:
        "Process a list of `texts`."
        if self.n_cpus <= 1: return self._process_all_1(texts)
        with ProcessPoolExecutor(self.n_cpus) as e:
            return sum(e.map(self._process_all_1, partition_by_cores(texts, self.n_cpus)), [])


def save_texts(paths, filename, lang):
    classes = ['unsup']
    file_count = 0
    filename = filename + '_' + lang + '.csv'
    if os.path.isfile(filename):
        os.remove(filename)
    with open(filename, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
        for idx, label in enumerate(classes):
            for path in paths:
                for fname in (path).glob('*'):
                    file_count += 1
                    print('writing from %s' % fname)
                    [writer.writerow([line, idx]) for line in fname.open('r', encoding='utf-8').read().split('\n')]
    print('%d texts saved to %s' % (file_count, filename))


def get_tokens(filename):
    data = pd.read_csv(filename, header=None, escapechar='\\', chunksize=500000)
    for idx, df in enumerate(data):
        print(idx)
        yield VocabularyTokenizer().process_all(df[0].astype(str))


def filter_currency(array: list) -> list:
    filtered = [item for item in array if not re.match(
        pattern=r"(?<![.,])(?:- *)?\b[0-9]{1,3}(?:\.?[0-9]{3})*\,?[0-9]{2}(?![.,-])\b|(?<![.,])(?:- *)?\b[0-9]{1,3}(?:,?[0-9]{3})*\.[0-9]{2}(?![.,-])\b",
        string=item)]
    print('Size before filtering currency: %d, Size after filtering currency: %d' % (len(array), len(filtered)))
    return filtered


def filter_doc_id(array: list) -> list:
    filtered = [doc_id for doc_id in array if not (
            re.match(pattern=r"\b[0-9a-f]{6,7}\b", string=doc_id) and not re.match(pattern=r"\b[a-f]{6,7}\b",
                                                                                   string=doc_id))]
    print('Size before filtering doc ids: %d, Size after filtering doc ids: %d' % (len(array), len(filtered)))
    return filtered


def filter_processes(array: list) -> list:
    filtered = [item for item in array if
                not re.match(pattern='\d{7}-\d{2}.\d{4}.\d{1}.\d{2}.\d{4}', string=item)]
    print('Size before filtering processes: %d, Size after filtering processes: %d' % (len(array), len(filtered)))
    return filtered


def write_list(array: list, path_out: Path):
    array.insert(0, '<UNK>')
    array.insert(0, '<S>')
    array.insert(0, '</S>')
    with path_out.open(mode='w', encoding='utf8') as file:
        for item in array:
            file.write(item + '\n')
    file.close()


def get_freq_filename(corpus_prefix: str, lang: str = 'pt'):
    return 'freq_' + corpus_prefix + '_' + lang + '.pickle'


def generate_vocabulary(corpus_prefix: str, path_in: str, lang: str = 'pt', min_count: int = 3,
                        discard_currency: bool = False, discard_processes: bool = False,
                        discard_doc_ids: bool = False) -> None:
    """
    :param corpus_prefix: Prefix identifying the corpus for training
    :param path_in: Example:
                        Path('/media/discoD/repositorios/1-billion-word-language-modeling-benchmark/')
    :param path_out: Example:
                        Path('/media/discoD/repositorios/1-billion-word-language-modeling-benchmark/vocabulary.txt')
    :param lang: Language of the model for training
    :param min_count: Minimum count of occurrences for the words to be added to the vocabulary
    :param discard_currency: Determine if currency values should be filtered out
    :param discard_processes: Determine if process numbers should be filtered out
    :param discard_doc_ids: Determine if document ids should be filtered out
    :return:
    """
    print('Reading data from %s' % path_in)
    path_in = Path(path_in)
    file_out = 'vocabulary_' + corpus_prefix + '_' + lang + '.txt'
    file_original_out = 'vocabulary_original_' + corpus_prefix + '_' + lang + '.txt'
    path_out = Path(path_in) / file_out
    path_original_out = Path(path_in) / file_original_out
    freq_filename = get_freq_filename(corpus_prefix, lang)
    freq_file = path_in / freq_filename

    if not freq_file.exists():

        if not path_out.exists():
            training_folder = 'training-' + corpus_prefix
            heldout_folder = 'heldout-' + corpus_prefix

            save_texts([path_in / training_folder], 'train_' + corpus_prefix, lang)
            save_texts([path_in / heldout_folder], 'test_' + corpus_prefix, lang)

            save_texts([path_in / training_folder, path_in / heldout_folder], 'full_' + corpus_prefix, lang)

        full_file = 'full_' + corpus_prefix + '_' + lang + '.csv'
        freq_full = Counter(p for o in chain.from_iterable(get_tokens(full_file)) for p in o)

        with freq_file.open(mode='wb') as f:
            pickle.dump(freq_full, f)
        f.close()

    else:
        with freq_file.open(mode='rb') as f:
            freq_full = pickle.load(f)
        f.close()

    total_number_of_tokens = sum(freq_full.values())
    print('Total number of tokens: %d' % total_number_of_tokens)

    original_vocabulary = sorted([palavra for palavra, contagem in freq_full.most_common()])
    original_vocabulary_length = len(original_vocabulary)
    print('Original vocabulary length: %d' % original_vocabulary_length)
    write_list(original_vocabulary, path_original_out)

    filtered = [palavra for palavra, contagem in freq_full.most_common() if contagem >= min_count]
    print('Total of words that occurred more than or equal %d times: %d' % (min_count, len(filtered)))

    if discard_currency:
        filtered = filter_currency(filtered)

    if discard_processes:
        filtered = filter_processes(filtered)

    if discard_doc_ids:
        filtered = filter_doc_id(filtered)

    write_list(sorted(filtered), path_out)
    print('Final length of the vocabulary: %d' % len(filtered))
    print('Number of training tokens: %d' % total_number_of_tokens)


if __name__ == '__main__': fire.Fire(generate_vocabulary)
