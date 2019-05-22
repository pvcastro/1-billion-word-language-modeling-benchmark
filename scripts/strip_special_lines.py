import re, sys, codecs, nltk

if len(sys.argv) >= 4:
    caminho_entrada = sys.argv[1]
    caminho_saida = sys.argv[2]
    caminho_especiais = sys.argv[3]
    print(sys.argv)
if len(sys.argv) == 5:
    tamanho_minimo_sentencas = sys.argv[4]
else:
    print("Usage: python strip_special_lines.py caminho_entrada caminho_saida caminho_especiais")
    sys.exit()


sent_tokenizer = nltk.data.load('tokenizers/punkt/portuguese.pickle')


def evitar_linhas_pequenas(line, tamanho_minimo_sentencas, writer):
    for sent in sent_tokenizer.tokenize(line):
        if sent.count(' ') >= tamanho_minimo_sentencas and sent[-1] in ['.', '!', '?', ';']:
            if sent[0:2] == '- ':
                sent = sent[2:]
            elif sent[0] == ' ' or sent[0] == '-':
                sent = sent[1:]
            writer.write(sent)
            return 1
    return 0


def remover_linhas_especiais(caminho_entrada, caminho_saida, caminho_especiais, tamanho_minimo_sentencas):
    count_clean = 0
    count_especiais = 0
    output_clean = codecs.open(caminho_saida, "w", 'utf-8')
    output_especiais = codecs.open(caminho_especiais, "w", 'utf-8')
    for line in codecs.open(caminho_entrada, 'r', 'utf-8'):
        # if not re.fullmatch("^[\W_]+$", line):
        if not re.match("^[^a-zA-Z]+$", line):
            if tamanho_minimo_sentencas:
                wrote = evitar_linhas_pequenas(line, tamanho_minimo_sentencas, output_clean)
                if wrote == 0:
                    output_especiais.write(line)
                    count_especiais = count_especiais + 1
                else:
                    count_clean = count_clean + 1
            else:
                output_clean.write(line)
                count_clean = count_clean + 1
        else:
            output_especiais.write(line)
            count_especiais = count_especiais + 1
    print("Escritas %d linhas de %s em %s" % (count_clean, caminho_entrada, caminho_saida))
    print("Escritas %d linhas de %s em %s" % (count_especiais, caminho_entrada, caminho_especiais))
    output_clean.close()
    output_especiais.close()


remover_linhas_especiais(caminho_entrada, caminho_saida, caminho_especiais, tamanho_minimo_sentencas)
