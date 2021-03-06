"""
Script to merge
"""

import fire, math, html
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


def write_file(output_path, anexo_iter, num_tokens, max_tokens_per_setting, token_count):
    j = 0
    setting_token_count = 0
    for i, anexo in enumerate(anexo_iter):
        j += 1
        filename = anexo['IdDocumentoCompleto'] + '.txt'
        tribunal = str(anexo['Tribunal']).zfill(2)
        ano = str(anexo['Ano'])
        file_path = output_path / ano / tribunal
        if not file_path.exists():
            file_path.mkdir(exist_ok=True, parents=True)
        file_path = file_path / filename
        print(f'Writing to {file_path}...')
        text = anexo['Texto']
        with file_path.open(mode='w', encoding='utf8') as file_out:
            for line in split_by_break(text):
                file_out.write(html.unescape(line).replace('\xa0', ' ') + '\n')
        file_out.close()

        # calculate approximate length based on tokens
        text_len = len(text.split())
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
    print('{}. # documents: {:,}. # tokens: {:,}.'.format(output_path, j + 1, token_count['count']))


def clear(path_to_clear: Path) -> int:
    count = 0
    for file in path_to_clear.glob('*'):
        if file.is_file():
            file.unlink()
            count += 1
        else:
            count += clear(file)
    return count


def main(output, num_tokens=100000000):
    output_path = Path(output + '/documents')
    if not output_path.exists():
        print(f'Error: {output_path} does not exist. Creating.')
        output_path.mkdir(exist_ok=True, parents=True)
    else:
        print(f'{output_path} exists. Cleaning.')
        count = clear(output_path)
        print('Removed %s files from %s' % (count, str(output_path)))

    anos, regioes = get_anos_tipos_regioes()

    token_count = {'count': 0}

    max_tokens_per_setting = math.ceil(num_tokens / len(list(product(anos, regioes))))

    for ano, regiao in product(anos, regioes):
        print('Searching documents for ano %d, regiao %d' % (ano, regiao))
        write_file(output_path, AnexoIterable(ano=ano, regiao=regiao, request_timeout=60,
                                              elasticsearch_host='https://elastic.datalawyer.com.br:9200'),
                   num_tokens=num_tokens, max_tokens_per_setting=max_tokens_per_setting, token_count=token_count)


if __name__ == '__main__': fire.Fire(main)
