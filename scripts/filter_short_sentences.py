import sys, codecs
from split_text import split

if len(sys.argv) >= 4:
    caminho_entrada = sys.argv[1]
    caminho_saida = sys.argv[2]
    caminho_curtas = sys.argv[3]
    print(sys.argv)
else:
    print("Usage: python strip_special_lines.py caminho_entrada caminho_saida caminho_especiais")
    sys.exit()


def remover_linhas_curtas(caminho_entrada, caminho_saida, caminho_curtas):
    count_clean = 0
    count_curtas = 0
    output_clean = codecs.open(caminho_saida, "w", 'utf-8')
    output_curtas = codecs.open(caminho_curtas, "w", 'utf-8')
    for line in codecs.open(caminho_entrada, 'r', 'utf-8'):
        for sent in split(line, True):
            if sent.count(' ') >= 3:
                if sent[0:2] == '- ':
                    sent = sent[2:]
                elif sent[0] == ' ' or sent[0] == '-':
                    sent = sent[1:]
                output_clean.write(sent)
                count_clean = count_clean + 1
            else:
                output_curtas.write(line)
                count_curtas = count_curtas + 1
    print("Escritas %d linhas de %s em %s" % (count_clean, caminho_entrada, caminho_saida))
    print("Escritas %d linhas de %s em %s" % (count_curtas, caminho_entrada, caminho_curtas))
    output_clean.close()
    output_curtas.close()


remover_linhas_curtas(caminho_entrada, caminho_saida, caminho_curtas)
