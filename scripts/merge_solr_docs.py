"""
Script to merge
"""

import fire
from pathlib import Path
import numpy as np
from solr_util import AnexoIterable
from datetime import datetime
from itertools import product
from split_text import split_by_break


def get_anos_tipos_regioes():
    anos = np.arange(datetime.today().year, 2013, -1)
    tipos = ['Ata de Audiencia', 'Sentenca', 'Acordao']
    regioes = np.arange(1, 25, 1)
    regioes = np.delete(regioes, 1, 0)
    return anos, tipos, regioes


def write_file(full_path, ano_regiao_path, anexo_iter, num_tokens):
    total_num_tokens = 0
    print(f'Writing to {full_path} and {ano_regiao_path}...')
    j = 0
    full_out = open(full_path, 'a', encoding='utf-8')
    ano_regiao_out = open(ano_regiao_path, 'a', encoding='utf-8')
    for i, anexo in enumerate(anexo_iter):
        j += 1
        for line in split_by_break(anexo['texto']):
            full_out.write(line + '\n')
            ano_regiao_out.write(line + '\n')

        # calculate approximate length based on tokens
        total_num_tokens += len(anexo['texto'].split())
        if total_num_tokens > num_tokens:
            break
        if (i + 1) % 10000 == 0:
            print('Processed {:,} documents. Total # tokens: {:,}.'.format(i + 1, total_num_tokens))
    print('{}. # documents: {:,}. # tokens: {:,}.'.format(full_path, j, total_num_tokens))


def main(output, docs_per_group=10000, num_tokens=100000000):
    output = Path(output + '/full')
    if not output.exists():
        print(f'Error: {output} does not exist. Creating.')
        output.mkdir(exist_ok=True)

    full_path = output.joinpath('full.csv')

    anos, tipos, regioes = get_anos_tipos_regioes()

    if full_path.exists():
        full_path.unlink()
    for ano, tipo, regiao in product(anos, tipos, regioes):
        full_ano_regiao_path = output.joinpath('full_' + str(ano) + '_' + str(regiao) + '.csv')
        if full_ano_regiao_path.exists():
            full_ano_regiao_path.unlink()
        write_file(full_path, full_ano_regiao_path,
                   AnexoIterable(ano=ano, tipo=tipo, regiao=regiao, limit=docs_per_group),
                   num_tokens=num_tokens)


if __name__ == '__main__': fire.Fire(main)
