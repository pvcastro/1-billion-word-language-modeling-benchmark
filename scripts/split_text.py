# -*- coding: utf-8 -*-
import re, string, collections, sys, codecs
import pandas as pd
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters, PunktLanguageVars
from pathlib import Path


def split_texts_by_sentences(path_in, path_out):
    text_count = 0
    sentence_count = 0
    output = codecs.open(path_out, "w", 'utf-8')
    for line in codecs.open(path_in, 'r', 'utf-8'):
        text_count += 1
        sentences = split(line)
        if len(sentences) > 0:
            for sentence in sentences:
                output.write(sentence + "\n")
                sentence_count += 1
        else:
            output.write("\n")
    print("Wrote %d lines from %d texts from file %s" % (sentence_count, text_count, path_in))
    output.close()


class CustomVars(PunktLanguageVars):
    sent_end_chars = ('.', '?', '!', ';')


def sentence_tokenize(sentence_tokenizer, text):
    return [multi_replace(sentence, replacements_rev, ignore_case=True) for sentence in sentence_tokenizer.tokenize(
        multi_replace(text, replacements, ignore_case=True))]


def multi_replace(string, replacements, ignore_case=False):
    """
    Given a string and a dict, replaces occurrences of the dict keys found in the
    string, with their corresponding values. The replacements will occur in "one pass",
    i.e. there should be no clashes.
    :param str string: string to perform replacements on
    :param dict replacements: replacement dictionary {str_to_find: str_to_replace_with}
    :param bool ignore_case: whether to ignore case when looking for matches
    :rtype: str the replaced string
    """
    if ignore_case:
        replacements = dict((pair[0].lower(), pair[1]) for pair in sorted(replacements.items()))
    rep_sorted = sorted(replacements, key=lambda s: (len(s), s), reverse=True)
    rep_escaped = [re.escape(replacement) for replacement in rep_sorted]
    pattern = re.compile("|".join(rep_escaped), re.I if ignore_case else 0)
    return pattern.sub(lambda match: replacements[match.group(0).lower() if ignore_case else match.group(0)], string)


def split_by_break(text):
    text = re.sub(r'[“”]', '"', text)
    return [sentence.strip() for sentence in text.splitlines()]


def starts_with(quote_char, starting_text, text):
    return text.startswith(quote_char + starting_text)


def sanitize_segment(text, quote_chars=None, segments=None):
    if quote_chars is None:
        quote_chars = ['"', '\'']
    if segments is None:
        segments = [' (...),', ' (...);', ' (...)', '(...)', '[...]', ' ...', '...', '()', '),', ');', ')', ' ,', ' ;',
                   ' -', '•', ',', ';']
    text = text.strip()
    for quote_char in quote_chars:
        for segment in segments:
            if text.count(quote_char) == 1:
                if starts_with(quote_char, segment, text):
                    text = text.replace(quote_char + segment, '')
            elif text.count(quote_char) == 2:
                if text.startswith(quote_char):
                    if text.endswith(quote_char):
                        text = text[1:-1]
                        assert text.count(quote_char) == 0
                        text = text.replace(segment, '')
                    elif text.endswith(quote_char + '.'):
                        text = text[1:-2]
                        assert text.count(quote_char) == 0
                        text = text.replace(segment, '')
        if text.startswith(quote_char):
            patterns = ['\d+\.*', '^(\-*\d\s*\.*)*\-*\)*']
            for pattern in patterns:
                if re.fullmatch(pattern, text[1:]):
                    text = re.sub(pattern, '', text)[1:]
    return text.strip()


def split_by_sentence(text, use_semicolon=False):
    if use_semicolon:
        sentence_tokenizer = PunktSentenceTokenizer(punkt_param, lang_vars=CustomVars())
    else:
        sentence_tokenizer = PunktSentenceTokenizer(punkt_param)
    if type(text) == str:
        text = re.sub(r'[“”]', '"', text)
        return [sanitize_segment(paragraph) for paragraph in sentence_tokenize(sentence_tokenizer, text)]
    elif isinstance(text, collections.Iterable):
        result = []
        for subtext in text:
            subtext = re.sub(r'[“”]', '"', subtext)
            result.extend(split_by_sentence(subtext, use_semicolon))
        return result


def split(text, use_semicolon=False):
    segments_by_break = split_by_break(text)
    return split_by_sentence(segments_by_break, use_semicolon)


if __name__ == '__main__':
    if len(sys.argv) == 4:
        path_in = sys.argv[1]
        path_out = sys.argv[2]
        path_nbp = sys.argv[3]
        print(sys.argv)
    else:
        print("Usage: python split_text.py path_in path_out")
        sys.exit()

    punkt_param = PunktParameters()
    punkt_param.abbrev_types = set(pd.read_csv(path_nbp, header=None)[0].values)
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    replacements = {"Dr(a)": "Dr_a_", "Sr(a)": "Sr_a_", "Exmo(a)": "Exmo_a_"}
    replacements_rev = {value: key for (key, value) in replacements.items()}

    split_texts_by_sentences(path_in, path_out)
