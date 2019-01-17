"""
Script to merge
"""

import fire
from pathlib import Path
import csv
import numpy as np
from elasticsearch_util import AnoIterable, AnexoIterable
from sklearn.model_selection import train_test_split
from datetime import datetime
import pandas as pd
from itertools import product


def train_test_valid_split(dataframe, train_size):
    train_df, test_df = train_test_split(dataframe, train_size=train_size, test_size=1 - train_size, shuffle=True)
    test_df, valid_df = train_test_split(test_df, train_size=0.5, test_size=0.5, shuffle=True)
    return train_df, test_df, valid_df


def get_anos_regioes():
    regioes = np.arange(1, 25, 1)
    anos = np.arange(datetime.today().year, 1996, -1)
    return anos, regioes


def write_file(full_path, ano_regiao_path, anexo_iter, num_tokens):
    total_num_tokens = 0
    print(f'Writing to {full_path} and {ano_regiao_path}...')
    j = 0
    full_out = open(full_path, 'a', encoding='utf-8')
    ano_regiao_out = open(ano_regiao_path, 'a', encoding='utf-8')
    full_writer = csv.writer(full_out)
    ano_regiao_writer = csv.writer(ano_regiao_out)
    for i, anexo in enumerate(anexo_iter):
        j += 1
        full_writer.writerow([anexo['corpo']])
        ano_regiao_writer.writerow([anexo['corpo']])

        # calculate approximate length based on tokens
        total_num_tokens += len(anexo['corpo'].split())
        if total_num_tokens > num_tokens:
            break
        if i % 10000 == 0:
            print('Processed {:,} documents. Total # tokens: {:,}.'.format(i, total_num_tokens))
    print('{}. # documents: {:,}. # tokens: {:,}.'.format(full_path, j, total_num_tokens))


def main(output, docs_per_year_region=10000, num_tokens=100000000):
    output = Path(output + '/full')
    if not output.exists():
        print(f'Error: {output} does not exist. Creating.')
        output.mkdir(exist_ok=True)

    train_path = output.joinpath('train.csv')
    valid_path = output.joinpath('valid.csv')
    test_path = output.joinpath('test.csv')
    full_path = output.joinpath('full.csv')

    anos, regioes = get_anos_regioes()

    if full_path.exists():
        full_path.unlink()
    for ano, regiao in product(anos, regioes):
        full_ano_regiao_path = output.joinpath('full_' + str(ano) + '_' + str(regiao) + '.csv')
        if full_ano_regiao_path.exists():
            full_ano_regiao_path.unlink()
        write_file(full_path, full_ano_regiao_path, AnexoIterable(ano=ano, regiao=regiao, limit=docs_per_year_region),
                   num_tokens=num_tokens)

    #write_file(full_path, AnoIterable(anos, regioes, limit=docs_per_year_region), num_tokens)

    train_df, test_df, valid_df = train_test_valid_split(pd.read_csv(full_path, header=None), train_size=0.7)
    train_df.to_csv(train_path, header=None, index=None)
    test_df.to_csv(test_path, header=None, index=None)
    valid_df.to_csv(valid_path, header=None, index=None)

    # write_file(train_path, AnoIterable(anos_treino, regioes), num_tokens)
    # write_file(valid_path, AnoIterable(anos_validacao, regioes), num_tokens/10)
    # write_file(test_path, AnoIterable(anos_teste, regioes), num_tokens / 10)


if __name__ == '__main__': fire.Fire(main)
