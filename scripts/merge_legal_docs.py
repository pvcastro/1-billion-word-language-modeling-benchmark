"""
Script to merge
"""

import fire, math
from pathlib import Path
import numpy as np
from elasticsearch_util import AnexoIterable
from datetime import datetime
from itertools import product
from split_text import split_by_break


def get_anos_tipos_regioes():
    anos = np.arange(datetime.today().year, 2013, -1)
    # tipos = ["Acórdão", "Sentença", "Ata da Audiência"]
    regioes = np.arange(1, 25, 1)
    return anos, regioes


def write_file(full_path, anexo_iter, num_tokens, max_tokens_per_setting, token_count):
    print(f'Writing to {full_path}...')
    j = 0
    full_out = open(full_path, 'a', encoding='utf-8')
    setting_token_count = 0
    for i, anexo in enumerate(anexo_iter):
        j += 1
        for line in split_by_break(anexo['Texto']):
            full_out.write(line + '\n')

        # calculate approximate length based on tokens
        text_len = len(anexo['Texto'].split())
        token_count['count'] += text_len
        setting_token_count += text_len
        if token_count['count'] > num_tokens or setting_token_count > max_tokens_per_setting:
            break
        if (i + 1) % 100 == 0:
            print('Processed {:,} documents for region {} and year {}. Total # tokens: {:,}.'.format(i + 1,
                                                                                                     anexo_iter.regiao,
                                                                                                     anexo_iter.ano,
                                                                                                     token_count[
                                                                                                         'count']))
    print('{}. # documents: {:,}. # tokens: {:,}.'.format(full_path, j + 1, token_count['count']))
    full_out.close()


def main(output, num_tokens=100000000):
    output = Path(output + '/full')
    if not output.exists():
        print(f'Error: {output} does not exist. Creating.')
        output.mkdir(exist_ok=True)

    full_path = output.joinpath('full.csv')

    anos, regioes = get_anos_tipos_regioes()

    if full_path.exists():
        full_path.unlink()

    token_count = {'count': 0}

    max_tokens_per_setting = math.ceil(num_tokens / len(list(product(anos, regioes))))

    for ano, regiao in product(anos, regioes):
        print('Searching documents for ano %d, regiao %d' % (ano, regiao))
        write_file(full_path, AnexoIterable(ano=ano, regiao=regiao, request_timeout=60),
                   num_tokens=num_tokens, max_tokens_per_setting=max_tokens_per_setting, token_count=token_count)


if __name__ == '__main__': fire.Fire(main)
