"""
Script used for cleaning corpus in order to train word embeddings.

All emails are mapped to a EMAIL token.
All numbers are mapped to 0 token.
All urls are mapped to URL token.
Different quotes are standardized.
Different hiphen are standardized.
HTML strings are removed.
All text between brackets are removed.
All sentences shorter than 5 tokens were removed.
...
"""

import re, argparse
from datetime import datetime

# Punctuation list
punctuations = re.escape('!"#%\'()*+,./:;<=>?@[\\]^_`{|}~')

# ##### #
# Regex #
# ##### #
re_remove_brackets = re.compile(r'\{.*\}')
re_remove_html = re.compile(r'<(\/|\\)?.+?>', re.UNICODE)
re_transform_numbers = re.compile(r'\d', re.UNICODE)
re_transform_emails = re.compile(r'[^\s]+@[^\s]+', re.UNICODE)
re_transform_url = re.compile(r'(http|https)://[^\s]+', re.UNICODE)
# Different quotes are used.
re_quotes_1 = re.compile(r"(?u)(^|\W)[‘’′`']", re.UNICODE)
re_quotes_2 = re.compile(r"(?u)[‘’`′'](\W|$)", re.UNICODE)
re_quotes_3 = re.compile(r'(?u)[‘’`′“”]', re.UNICODE)
re_dots = re.compile(r'(?<!\.)\.\.(?!\.)', re.UNICODE)
re_punctuation = re.compile(r'([,";:]){2},', re.UNICODE)
re_hiphen = re.compile(r' -(?=[^\W\d_])', re.UNICODE)
re_tree_dots = re.compile(u'…', re.UNICODE)
# Differents punctuation patterns are used.
re_punkts = re.compile(r'(\w+)([%s])([ %s])' %
                       (punctuations, punctuations), re.UNICODE)
re_punkts_b = re.compile(r'([ %s])([%s])(\w+)' %
                         (punctuations, punctuations), re.UNICODE)
re_punkts_c = re.compile(r'(\w+)([%s])$' % (punctuations), re.UNICODE)
re_changehyphen = re.compile(u'–')
re_doublequotes_1 = re.compile(r'(\"\")')
re_doublequotes_2 = re.compile(r'(\'\')')
re_trim = re.compile(r' +', re.UNICODE)


def log(message):
    print(datetime.now(), '-', message)


def clean_text(text):
    """Apply all regex above to a given string."""
    text = text.lower()
    text = text.replace('\xa0', ' ')
    text = re_tree_dots.sub('...', text)
    text = re.sub('\.\.\.', '', text)
    text = re_remove_brackets.sub('', text)
    text = re_changehyphen.sub('-', text)
    text = re_remove_html.sub(' ', text)
    text = re_transform_numbers.sub('0', text)
    text = re_transform_url.sub('URL', text)
    text = re_transform_emails.sub('EMAIL', text)
    text = re_quotes_1.sub(r'\1"', text)
    text = re_quotes_2.sub(r'"\1', text)
    text = re_quotes_3.sub('"', text)
    text = re.sub('"', '', text)
    text = re_dots.sub('.', text)
    text = re_punctuation.sub(r'\1', text)
    text = re_hiphen.sub(' - ', text)
    text = re_punkts.sub(r'\1 \2 \3', text)
    text = re_punkts_b.sub(r'\1 \2 \3', text)
    text = re_punkts_c.sub(r'\1 \2', text)
    text = re_doublequotes_1.sub('\"', text)
    text = re_doublequotes_2.sub('\'', text)
    text = re_trim.sub(' ', text)
    return text.strip()


if __name__ == '__main__':
    # Parser descriptors
    parser = argparse.ArgumentParser(
        description='''Script used for cleaning corpus in order to train
        word embeddings.''')

    parser.add_argument('input',
                        type=str,
                        help='input text file to be cleaned')

    parser.add_argument('output',
                        type=str,
                        help='output text file')

    args = parser.parse_args()
    f_in = args.input
    f_out = args.output

    txt, wc_l, written = [], 0, 0
    final = []

    with open(f_in, 'r', encoding='utf8') as f:
        log('Counting lines...')
        wc_l = sum(1 for l in f)
        log('Counted %d lines' % wc_l)

    # Clean lines.
    with open(f_out, 'w', encoding='utf8') as fp:
        with open(f_in, 'r', encoding='utf8') as f:
            log('Cleaning lines...')
            for i, line in enumerate(f):
                # if not re.match("^[^a-zA-Z]+$", line):
                clean_line = clean_text(line)
                if clean_line.count(' ') >= 3:
                    if clean_line[0:2] == '- ':
                        clean_line = clean_line[2:]
                    elif clean_line[0] == ' ' or clean_line[0] == '-':
                        clean_line = clean_line[1:]
                    fp.write(clean_line + '\n')
                    written += 1
                if (i + 1) % 100000 == 0:
                    log('Cleaned %d of %d' % (i + 1, wc_l))
    log('Finished writing %d from %d lines' % (written, wc_l))
