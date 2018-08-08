import re, sys, codecs

if len(sys.argv) == 4:
    caminho_entrada = sys.argv[1]
    caminho_saida = sys.argv[2]
    caminho_especiais = sys.argv[3]
    print(sys.argv)
else:
    print("Usage: python strip_special_lines.py caminho_entrada caminho_saida caminho_especiais")
    sys.exit()


def remover_linhas_especiais(caminho_entrada, caminho_saida, caminho_especiais):
    count_clean = 0
    count_especiais = 0
    output_clean = codecs.open(caminho_saida, "w", 'utf-8')
    output_especiais = codecs.open(caminho_especiais, "w", 'utf-8')
    for line in codecs.open(caminho_entrada, 'r', 'utf-8'):
        # if not re.fullmatch("^[\W_]+$", line):
        if not re.match("^[^a-zA-Z]+$", line):
            output_clean.write(line)
            count_clean = count_clean + 1
        else:
            output_especiais.write(line)
            count_especiais = count_especiais + 1
    print("Escritas %d linhas de %s em %s" % (count_clean, caminho_entrada, caminho_saida))
    print("Escritas %d linhas de %s em %s" % (count_especiais, caminho_entrada, caminho_especiais))
    output_clean.close()
    output_especiais.close()


remover_linhas_especiais(caminho_entrada, caminho_saida, caminho_especiais)
