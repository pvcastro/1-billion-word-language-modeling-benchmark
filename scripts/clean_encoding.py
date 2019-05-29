import argparse
from datetime import datetime


def log(message):
    print(datetime.now(), '-', message)


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

    with open(f_in, 'r', encoding='utf8', errors='ignore') as f:
        log('Counting lines...')
        wc_l = sum(1 for l in f)
        log('Counted %d lines' % wc_l)

    # Clean lines.
    with open(f_out, 'w', encoding='utf8') as fp:
        with open(f_in, 'r', encoding='utf8', errors='ignore') as f:
            log('Cleaning lines...')
            written = 0
            for line in f:
                fp.write(line)
                written += 1
                if written % 500000 == 0:
                    log('Cleaned %d of %d' % (written, wc_l))
    log('Finished writing %d from %d lines' % (written, wc_l))
